from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator



MIN_PASSWORD_LENGTH = 8

MAX_PASSWORD_LENGTH = 128

MAX_NAME_LENGTH = 100





class RegisterRequest(BaseModel):

    name: str = Field(..., max_length=MAX_NAME_LENGTH)

    email: EmailStr

    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)



    @field_validator("name")

    @classmethod

    def name_not_blank(cls, value: str) -> str:

        value = value.strip()

        if not value:

            raise ValueError("Name is required.")

        if len(value) > MAX_NAME_LENGTH:

            raise ValueError(f"Name must be at most {MAX_NAME_LENGTH} characters.")

        return value



    @field_validator("password")

    @classmethod

    def password_strong_enough(cls, value: str) -> str:

        if len(value) < MIN_PASSWORD_LENGTH:

            raise ValueError(

                f"Password must be at least {MIN_PASSWORD_LENGTH} characters."

            )

        if len(value) > MAX_PASSWORD_LENGTH:

            raise ValueError(

                f"Password must be at most {MAX_PASSWORD_LENGTH} characters."

            )

        if value.isdigit() or value.isalpha():

            raise ValueError(

                "Password must include both letters and numbers."

            )

        return value





class LoginRequest(BaseModel):

    email: EmailStr

    password: str = Field(..., max_length=MAX_PASSWORD_LENGTH)





class UserOut(BaseModel):

    model_config = ConfigDict(from_attributes=True)



    id: int

    name: str

    email: str

    is_admin: bool = False





class AuthResponse(BaseModel):

    # Opaque session token — clients send it as Authorization: Bearer.

    access_token: str

    user: UserOut


