import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.db.models import User
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email, set_new_password, update_avatar
)
from src.schemas import UserModel


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

    # -----------------------------------------------------------------------------------------------------------------------------------
    async def test_get_user_by_email(self):
        email = "test@example.com"
        expected_user = User(email=email)
        self.session.query.return_value.filter.return_value.first.return_value = expected_user
        result = await get_user_by_email(email=email, db=self.session)
        self.assertEqual(result, expected_user)

    # -----------------------------------------------------------------------------------------------------------------------------------
    async def test_create_user(self):
        user_data = UserModel(
            username='Pavlo',
            email="test@example.com",
            password='123456789'
        )
        expected_user = User(**user_data.model_dump())
        created_user = await create_user(body=user_data, db=self.session)
        self.assertEqual(created_user.username, expected_user.username)
        self.assertEqual(created_user.email, expected_user.email)
        self.session.commit.assert_called_once()

    # -----------------------------------------------------------------------------------------------------------------------------------
    async def test_update_token(self):
        user = User()
        token = "new_token"
        await update_token(user=user, token=token, db=self.session)
        self.assertEqual(user.refresh_token, token)
        self.session.commit.assert_called_once()

    # -----------------------------------------------------------------------------------------------------------------------------------
    async def test_confirmed_email(self):
        email = "test@example.com"
        user = User(email=email)
        self.session.query.return_value.filter.return_value.first.return_value = user
        await confirmed_email(email=email, db=self.session)
        self.assertTrue(user.confirmed)
        self.session.commit.assert_called_once()

    # -----------------------------------------------------------------------------------------------------------------------------------
    async def test_update_avatar(self):
        user = User()
        url = "img.com"
        upd_user = await update_avatar(user.email, url, db=self.session)
        self.assertEqual(upd_user.avatar, url)
        self.session.commit.assert_called_once()

    # -----------------------------------------------------------------------------------------------------------------------------------
    async def test_set_new_password(self):
        user = User()
        password = "new_password"
        upd_user = await set_new_password(user.email, password, db=self.session)
        self.assertEqual(upd_user.password, password)
        self.session.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
