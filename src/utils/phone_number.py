from pydantic import BaseModel
import phonenumbers


class PhoneNumber(BaseModel):
    phone_number: str

    @classmethod
    def is_valid_phone_number(cls, phone_number):
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            return phonenumbers.is_valid_number(parsed_number)
        except phonenumbers.NumberParseException:
            return False

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_phone_number

    @classmethod
    def validate_phone_number(cls, v):
        if not cls.is_valid_phone_number(v):
            raise ValueError("Invalid phone number.")
        return v