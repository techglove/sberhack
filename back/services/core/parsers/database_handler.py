import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Session = sessionmaker()

class City(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<City(id={}, name={})>".format(id, name)


class MedOrganisation(Base):
    __tablename__ = 'med_organisations'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<MedOrganisation(id={}, name={})>".format(id, name)


class TestPlace(Base):
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('med_organisations.id'))
    city_id = Column(Integer, ForeignKey('cities.id'))
    address = Column(String)
    position_lat = Column(Float)
    position_lon = Column(Float)
    price = Column(String)
    url = Column(String)
    is_urgent = Column(Boolean)


class TestPlacePusher():
    def __init__(self, host, user, password, database):
        self.engine = sqlalchemy.create_engine("postgresql+psycopg2://{}:{}@{}/{}".format(user, password, host, database))
        self.session = Session.configure(bind=engine)

    def get_or_add_city(self, city_name):
        city = self.session.query(City).filter_by(name=city_name).first()
        if city:
            return city.id
        else:
            city = City(name=city_name)
            self.session.add(city)
            return city.id

    def get_or_add_med_org(self, med_org):
        org = self.session.query(MedOrganisation).filter_by(name=med_org).first()
        if org:
            return org.id
        else:
            org = MedOrganisation(name=med_org)
            self.session.add(org)
            return org.id

    def add_test_place(self, city, med_org, address, position, url, price, is_urgent=False):
        city_id = get_or_add_city(city)
        org_id = get_or_add_med_org(med_org)
        test_place = TestPlace(
            org_id = org_id,
            city_id = city_id,
            address = address,
            position_lat = position.lat,
            position_lon = position.lon,
            url = url,
            price = price,
            is_urgent = is_urgent
        )

        self.session.add(test_place)

