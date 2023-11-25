from typing import List

from fastapi import Depends, Query, APIRouter, status
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from src.db.models import User
from src.schemas import ContactRequest, ContactResponse
from src.db.db_connect import get_db
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=['contacts'])


@router.post("/", response_model=ContactResponse, description='No more than 5 request per minute',
             dependencies=[Depends(RateLimiter(times=5, seconds=60))], status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactRequest, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
        Create a new contact.

        :param contact: The contact data to create.
        :type contact: ContactRequest
        :param db: The database session.
        :type db: Session
        :param current_user: The current user.
        :type current_user: User
        :return: The newly created contact.
        :rtype: ContactResponse
    """
    contact = await repository_contacts.create_contact(contact, db, current_user)
    return contact


@router.get("/", response_model=List[ContactResponse], description='No more than 10 request per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
        Retrieve a list of contacts with specified pagination parameters.

        :param skip: The number of contacts to skip.
        :type skip: int
        :param limit: The maximum number of contacts to return.
        :type limit: int
        :param db: The database session.
        :type db: Session
        :param current_user: The current user.
        :type current_user: User
        :return: A list of contacts.
        :rtype: List[ContactResponse]
        """
    contacts = await repository_contacts.get_contacts(skip, limit, db, current_user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, description='No more than 10 request per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contact(contact_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
        Retrieve a contact by its ID.

        :param contact_id: The ID of the contact to retrieve.
        :type contact_id: int
        :param db: The database session.
        :type db: Session
        :param current_user: The current user.
        :type current_user: User
        :return: The retrieved contact.
        :rtype: ContactResponse
    """
    contact = await repository_contacts.get_contact(contact_id, db, current_user)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse, description='No more than 10 request per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(contact_id: int, updated_contact: ContactRequest,
                         db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
        Update a contact by its ID.

        :param contact_id: The ID of the contact to update.
        :type contact_id: int
        :param updated_contact: The updated contact data.
        :type updated_contact: ContactRequest
        :param db: The database session.
        :type db: Session
        :param current_user: The current user.
        :type current_user: User
        :return: The updated contact.
        :rtype: ContactResponse
    """
    contact = await repository_contacts.update_contact(contact_id, updated_contact, db, current_user)
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse, description='No more than 10 request per minute',
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def delete_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
        Delete a contact by its ID.

        :param contact_id: The ID of the contact to delete.
        :type contact_id: int
        :param db: The database session.
        :type db: Session
        :param current_user: The current user.
        :type current_user: User
        :return: The deleted contact.
        :rtype: ContactResponse
    """
    contact = await repository_contacts.delete_contact(contact_id, db, current_user)
    return contact


@router.get("/search", response_model=List[ContactResponse], description='No more than 10 request per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def search_contacts(
        q: str = Query(..., description="Search query for name, last name, or email"),
        skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
        Search contacts by name, last name, or email with specified pagination parameters.

        :param q: The search query.
        :type q: str
        :param skip: The number of contacts to skip.
        :type skip: int
        :param limit: The maximum number of contacts to return.
        :type limit: int
        :param db: The database session.
        :type db: Session
        :param current_user: The current user.
        :type current_user: User
        :return: A list of contacts matching the search query.
        :rtype: List[ContactResponse]
    """
    contacts = await repository_contacts.search_contacts(q, skip, limit, db, current_user)
    return contacts


@router.get("/birthdays/", response_model=List[ContactResponse], description='No more than 10 request per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def upcoming_birthdays(db: Session = Depends(get_db),
                             current_user: User = Depends(auth_service.get_current_user)):
    """
        Retrieve a list of upcoming birthdays for the current user.

        :param db: The database session.
        :type db: Session
        :param current_user: The current user.
        :type current_user: User
        :return: A list of contacts with upcoming birthdays.
        :rtype: List[ContactResponse]
    """
    upcoming_birthdays_this_year = await repository_contacts.upcoming_birthdays(db, current_user)
    return upcoming_birthdays_this_year
