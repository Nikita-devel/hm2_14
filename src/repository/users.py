from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.db.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
        Retrieve a user by their email address.

        :param email: The email address of the user to retrieve.
        :type email: str
        :param db: The database session.
        :type db: Session
        :return: The user with the specified email address.
        :rtype: User
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
       Create a new user with the provided user data.

       :param body: The user data to create.
       :type body: UserModel
       :param db: The database session.
       :type db: Session
       :return: The newly created user.
       :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
       Update the refresh token for a user.

       :param user: The user whose token is to be updated.
       :type user: User
       :param token: The new refresh token or None.
       :type token: str | None
       :param db: The database session.
       :type db: Session
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
       Confirm a user's email address.

       :param email: The email address to confirm.
       :type email: str
       :param db: The database session.
       :type db: Session
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User:
    """
        Update the avatar URL for a user.

        :param email: The email address of the user whose avatar is to be updated.
        :type email: str
        :param url: The new avatar URL.
        :type url: str
        :param db: The database session.
        :type db: Session
        :return: The user with the updated avatar URL.
        :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def set_new_password(email: str, new_password: str, db: Session):
    """
       Set a new password for a user.

       :param email: The email address of the user whose password is to be updated.
       :type email: str
       :param new_password: The new password.
       :type new_password: str
       :param db: The database session.
       :type db: Session
       :return: The user with the updated password.
       :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.password = new_password
    db.commit()
    return user
