# login_steps.py
# see: https://behave.readthedocs.io/

from behave import *
from selenium.webdriver.common.by import By

@given(u'I open the url "{url}"')
def open_webpage(context, url):
    context.driver.get(url)

@then(u'I expect that the title is "{title}"')
def check_title(context, title):
    assert context.driver.title == title

@when(u'I click on the "{link}" Link')
def click_link(context, link):
    context.driver.find_element(By.LINK_TEXT, link).click()

@when(u'I enter user "{user}" with password "{password}"')
def login_user(context,user,password):
    d=context.driver
    d.find_element(By.ID, 'email').send_keys(user)
    d.find_element(By.ID, 'password').send_keys(password)
    d.find_element(By.ID, 'submit').click()

@when(u'I enter the admin credentials')
def login_admin(context):
    login_user(context, context.config.ADMIN_USER, context.config.ADMIN_PASSWORD)

@then(u'I am logged in')
def i_am_logged_in(context):
    context.driver.find_element(By.LINK_TEXT, 'Abmelden')