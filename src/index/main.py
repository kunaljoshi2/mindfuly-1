from fastapi import Depends, HTTPException
from nicegui import ui
from pydantic import parse_obj_as
from contextlib import contextmanager
import logging
import copy

from src.mindfuly.routes.users import create_user
from user_service_v2.models.user import UserSchema, get_user_repository_v2, UserRepositoryV2

logger = logging.getLogger('uvicorn.error')

@ui.page('/home')
async def home_page():
    with ui.column().classes('mx-auto'):
        with ui.row().classes('w-full justify-center items-center px-4 mb-4'):
            ui.label('Mindfuly').classes('text-2xl font-bold')

        with ui.row().classes('w-full justify-between items-center mt-32 gap-4'):
            ui.button('Login', on_click=lambda: ui.navigate.to('/login')).classes('bg-blue-500')
            ui.button('Signup', on_click=lambda: ui.navigate.to('/signup')).classes('bg-blue-500')


@ui.page("/login")
async def login_page(user_repo: UserRepositoryV2 = Depends(get_user_repository_v2)):
    with ui.column().classes('mx-auto'):
        with ui.row().classes('w-full justify-center items-center px-4 mb-4'):
            ui.label('Login Page').classes('text-2xl font-bold mb-4')

        with ui.row().classes('w-full justify-center items-center'):
            username_input = ui.input('Username').classes('mb-2')
            password_input = ui.input('Password', password=True).classes('mb-4')

            error_label = ui.label().classes('text-red-500 mt-2')
            error_label.visible = False

            async def handle_login():
                user = await user_repo.get_by_name(username_input.value)

                if user == None:
                    ui.notify('Not a valid user!', color='red')
                    return

                if await user_repo.verify_password(user, password_input.value):

                    """
                    TODO:
                    Figure out how to navigate to a personalized page for each user.
                    """
                    
                    # ui.navigate.to('/{username}/overview')
                    pass 
                else:
                    error_label.text = "Invalid password. Please try again."
                    error_label.visible = True
                    password_input.value = ""
                    password_input.focus()

            ui.button('Login', on_click=handle_login).classes('mt-4')

            password_input.on('keydown.enter', handle_login)


@ui.page("/signup")
async def signup_page(user_repo: UserRepositoryV2 = Depends(get_user_repository_v2)):
    with ui.column().classes('mx-auto'):
        with ui.row().classes('w-full justify-center items-center px-4 mb-4'):
            ui.label('Signup Page').classes('text-2xl font-bold mb-4')

        with ui.row().classes('w-full justify-center items-center'):
            username_input = ui.input('Username').classes('mb-2')
            email_input = ui.input('Email').classes('mb-2')
            password_input = ui.input('Password').classes('mb-4') # password=False for visibility when signing up
            
            async def handle_signup():
                if not username_input.value or not email_input.value or not password_input.value:
                    ui.notify('Please fill in all fields.', color='red')
                    return

                result = await user_repo.create(username_input.value, email_input.value, password_input.value, tier=1)
                if not result:
                    ui.notify('User already exists.', color='red')
                    return
                
                ui.notify('Signup Successful! Please log in.')
                ui.navigate.to('/login')

            ui.button('Signup', on_click=handle_signup).classes('mt-4') 


@ui.page('/')
async def root_page(): ui.navigate.to('/home') # Redirect root to home page