import dataclasses
from datetime import datetime
import re

@dataclasses.dataclass
class RawApartment:
    url: str
    title: str = None
    price: str = None
    mq: str = None
    rooms: str = None
    description: str = None
    image_url: str = None
    privato: bool = None

    def to_apartment(self):
        apt = Apartment(self.url)

        apt.title = self.title.strip()
        apt.price = float(re.sub('[^0-9]', '', self.price)) if self.price else None
        apt.mq = float(re.sub('[^0-9]', '', self.mq)) if self.mq else None
        apt.rooms = int(re.sub('[^0-9]', '', self.rooms)) if self.rooms else None
        apt.description = self.description.strip('" \n') if self.description else None
        # if apt.description:
        #     apt.description = apt.description.replace(r'\n', ' ')
        apt.image_url = self.image_url
        apt.privato = self.privato
        return apt


@dataclasses.dataclass
class Apartment:
    url: str = dataclasses.field(metadata={"key": True})
    title: str  = None
    price: float  = None
    mq: float  = None
    rooms: int = None
    description: str = None
    image_url: str = None
    first_seen: datetime = dataclasses.field(default_factory=datetime.now)
    privato: bool = None
