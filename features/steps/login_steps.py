# login_steps.py
# see: https://behave.readthedocs.io/

from behave import *
from selenium.webdriver.common.by import By
from behave.api.pending_step import StepNotImplementedError
from features.environment import webserver_port

@given(u'I am on the home page')
def step_impl(context):
    open_page(context, "")

@given(u'I am on the page "{page}"')
def open_page(context, page):
    if page and page[0]!='/':
        page = '/'+page
    context.driver.get(f"http://localhost:{webserver_port}{page}")
    #raise StepNotImplementedError(f'Given I am on the page "{page}"')

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
    login_user(context, context.app_config.ADMIN_USER, context.app_config.ADMIN_PASSWORD)

@then(u'I am logged in')
def i_am_logged_in(context):
    context.driver.find_element(By.LINK_TEXT, 'Abmelden')