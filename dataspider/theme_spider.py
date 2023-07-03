from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import pandas as pd
import time
from selenium.common.exceptions import TimeoutException,NoSuchElementException,NoSuchFrameException

# 配置浏览器
options = webdriver.ChromeOptions()         # 设置为开发者模式，防止被各大网站识别出来使用了Selenium
options.add_experimental_option('excludeSwitches', ['enable-automation'])            # 进入网页
browser = webdriver.Chrome(options=options)
wait = WebDriverWait(browser,2)
# Q：什么是Selenium的WebDriverWait？ 与sleep有什么区别？
browser.get('https://s.weibo.com/weibo?q=%E6%9D%8E%E7%BA%A2%E8%89%AF&Refer=SWeibo_box')
time.sleep(20)

list_ct = []  # 存储文章内容

while True:
    # 扫描文章内容,扫描一页，判断是否还有下一页
    wait.until(EC.presence_of_element_located(
        (By.XPATH, '//div[@class="card"]/div[@class="card-feed"]/div[@class="content"]')))
    # 获取博文列表
    list_el = browser.find_elements_by_xpath('//div[@class="card"]')
    time.sleep(2)
    try:
        for l in list_el:
            actor_url = actor_name = content = content_url = content_date = sg = zf = pl = dz = ''
            try:
                # 获取作者
                t = l.find_element_by_xpath(
                    './div[@class="card-feed"]/div[@class="content"]/div[@class="info"]/div[2]/a')
                actor_url = t.get_attribute('href')
                actor_name = t.text

                # 博文内容
                t = l.find_elements_by_xpath('./div[@class="card-feed"]/div[@class="content"]/p[@class="txt"]')
                if len(t) > 1:
                    content = t[1].get_attribute('innerText')
                else:
                    content = t[0].get_attribute('innerText')

                # 博文时间
                t = l.find_element_by_xpath('./div[@class="card-feed"]/div[@class="content"]/p[@class="from"]/a')
                content_url = t.get_attribute('href')
                content_date = t.text

                # 收藏、转发、评论、点赞
                t = l.find_elements_by_xpath('./div[@class="card-act"]/ul/li')
                sc = t[0].get_attribute('innerText')
                zf = t[1].get_attribute('innerText')
                pl = t[2].get_attribute('innerText')
                dz = t[3].get_attribute('innerText')
            except Exception as e:
                pass
            # 追加
            list_ct.append([actor_url, actor_name, content, content_url, content_date, sc, zf, pl, dz])

        # 输出当前页码
        try:
            t = browser.find_element_by_xpath('//a[@class="pagenum"]')
            print('扫描进行到', str(t.text))
        except:
            pass
        # 判断是否还有下一页
        # break
        try:
            t = browser.find_element_by_xpath('//div[@class="m-page"]/div/a[@class="next"]')
            # 点击下一页
            t.click()
        except:
            print('文章扫描结束')
            break
    except Exception as e:
        print('非正常结束:', str(e))

# 保存发表的文章，到excel
df = pd.DataFrame(list_ct, columns=['actor_url' , 'actor_name' , 'content' , 'content_url','content_date','sc','zf','pl','dz'])
# 去重
df.drop_duplicates(subset=['actor_url' , 'actor_name' , 'content' , 'content_url','content_date','sc','zf','pl','dz'],inplace = True)
with pd.ExcelWriter(r'themeSpider_articles.xlsx') as writer:
    df.to_excel(writer,index=False,sheet_name = 'Sheet1')


def deal_comment_content(content):
    rel = content = content.replace(":", "：")
    if content.find('：回复') != -1:
        lt = content.split('：', 2)
        rel = lt[len(lt) - 1]
    else:
        lt = content.split('：', 1)
        rel = lt[len(lt) - 1]
    return rel


# 获取WB_text内容
def get_comment_data(l):
    actor = actor_url = render = render_url = content = date = ''
    # 获取发表者
    t = l.find_element_by_xpath('./div[@class="WB_text"]/a[1]')
    actor_url = t.get_attribute('href')
    actor = t.text

    # 判断是否回复的评论
    try:
        t = l.find_element_by_xpath('./div[@class="WB_text"]/a[@render="ext"]')
        render_url = t.get_attribute('href')
        render = t.text
    except NoSuchElementException:
        pass

    # 读取评论内容
    t = l.find_element_by_xpath('./div[@class="WB_text"]')
    content = t.text
    content = deal_comment_content(content)

    # 读取评论日期
    t = l.find_element_by_xpath('./div[@class="WB_func clearfix"]/div[@class="WB_from S_txt2"]')
    date = t.text

    return [actor, actor_url, render, render_url, content, date]


# 滚动到最底部
def scroll_down():
    while True:
        sh1 = browser.execute_script("return document.body.scrollHeight;")
        browser.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        time.sleep(0.5)
        sh2 = browser.execute_script("return document.body.scrollHeight;")

        if sh1 == sh2:
            break


# 加载更多评论
def loading_all_comment():
    # 执行到最下，等待查看更多
    while True:
        scroll_down()
        try:
            morr_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="more_txt"]')))
            # 如果超时
            morr_btn.click()
            print('加载更多+1')
            time.sleep(0.5)
        except:
            print('执行到最底部')
            break


# 载入所有子评论
def loading_all_child_comment():
    while True:
        btns = browser.find_elements_by_xpath('//a[@action-type="click_more_child_comment_big"]')
        if len(btns) == 0:
            break
        for btn in btns:
            try:
                # browser.execute_script("arguments[0].click();", btn)
                ActionChains(browser).move_to_element(btn).click(btn).perform()  # 需要移动到该控件，点击才有效
                # btn.click()
                time.sleep(0.5)
            except:
                # 存在点了以后还没加载完的，直接忽略错误
                pass


err_url = []
list_comment = []
b = 0
for index, r in df.iterrows():
    b = b + 1
    if  b > 5 :
        time.sleep(2)
        b=0
        print('暂停一次')
    url = r.content_url
    #url = df.loc[2,'content_url']
    print('序号:',str(index),'开始执行：',url)
    browser.get(url)
    try:
        loading_all_comment()  # 载入所有评论
        loading_all_child_comment()  # 载入所有子评论
        print('打开所有评论')
        #等待内容
        wait.until(EC.presence_of_element_located((By.XPATH,'//div[@node-type="root_comment"]/div[@class="list_con"]')))
        list_el = browser.find_elements_by_xpath('//div[@node-type="root_comment"]/div[@class="list_con"]')
        # 遍历
        for l in list_el:
            # 获取博文信息
            c = get_comment_data(l)
            list_comment.append(c)
            # 获取博文评论信息
            list_child = l.find_elements_by_xpath('.//div[@node-type="child_comment"]//div[@class="list_con"]')
            for lc in list_child:
                c = get_comment_data(lc)
                list_comment.append(c)
    except TimeoutException:
        print('TimeoutException:',url)
    except NoSuchElementException:
        print('NoSuchElementException:',url)
    except:
        print('something wring:',url)
        err_url.append(url)
    #break


df = pd.DataFrame(list_comment, columns=['actor' , 'actor_url' , 'render' , 'render_url' , 'content' , 'date'])
# 去重
df.drop_duplicates(subset=['actor' , 'actor_url' , 'render' , 'render_url' , 'content' , 'date'],inplace = True)
with pd.ExcelWriter(r'themeSpider_comments.xlsx') as writer:
    df.to_excel(writer,index=False,sheet_name = 'Sheet1')
