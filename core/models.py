from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

Base = declarative_base()


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)

    @property
    def lat(self) -> float:
        return float(to_shape(self.geom).y)

    @property
    def lng(self) -> float:
        return float(to_shape(self.geom).x)
