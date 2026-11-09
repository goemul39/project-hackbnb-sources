from typing import List
from hashlib import md5
from database.init import db
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column()
    rooms: Mapped[List["Room"]] = relationship(back_populates="host_user")

    def __repr__(self):
        return f'<User {self.email!r}>'
    
    def to_dict(self):
        # D5: public representation. Never expose the e-mail (nor the password
        # hash) in API responses that are not tied to the authenticated user.
        return {
            "id": self.id,
            "name": self.name,
        }

    def to_private_dict(self):
        # Only for the authenticated user's own endpoints (e.g. /users/me).
        return {
            **self.to_dict(),
            "email": self.email,
        }

    def set_password(self, clear_password: str):
        self.password_hash = md5(clear_password.encode("utf-8")).hexdigest()
    
    def is_valid_password(self, clear_password: str) -> bool:
        clear_password_hash = md5(clear_password.encode("utf-8")).hexdigest()
        return clear_password_hash == self.password_hash
