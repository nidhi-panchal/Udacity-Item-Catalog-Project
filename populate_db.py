from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Base, Artist, Name, User

engine = create_engine('sqlite:///artists.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

user1 = User(name="Jimmy", email="JimmyJim@gmail.com", picture='none.png')
session.add(user1)
session.commit()

# Create Painters category and painters within the category
painters = Artist(style="Painter")
session.add(painters)
session.commit()

painter1 = Name(name="Vincent van Gogh", description="Dutch post-impressionist painter who created about 2,100 works",
                artist=painters, user=user1)
session.add(painter1)
session.commit()

painter2 = Name(name="Pablo Picasso", description="Spanish painter, sculptor, printmaker, ceramicist, stage designer, poet and playwright",
                artist=painters, user=user1)
session.add(painter2)
session.commit()


# Create Musicians category and musicians within the category
musicians = Artist(style="Musician")
session.add(musicians)
session.commit()

musician1 = Name(name="The Beatles", description="English rock band consisting of members John Lennon, Paul McCartney, George Harrison and Ringo Starr",
                 artist=musicians, user=user1)
session.add(musician1)
session.commit()

musician2 = Name(name="BTS", description="South Korean boy band consisting of members Namjoon Kim, Seokjin Kim, Yoongi Min, Hoseok Jung, Jimin Park, Taehyung Kim, and Jungkook Jeon",
                 artist=musicians, user=user1)
session.add(musician2)
session.commit()


# Create Dancers category and dancers within the category
dancers = Artist(style="Dancer")
session.add(dancers)
session.commit()

dancer1 = Name(name="Keone Madrid", description="Dancer and choreographer known for his joint YouTube channel called Keone and Mari",
               artist=dancers, user=user1)
session.add(dancer1)
session.commit()

dancer2 = Name(name="Dylan Mayoral", description="Dancer, choreographer, gymnast, and member of the dance crew Boyband",
               artist=dancers, user=user1)
session.add(dancer2)
session.commit()


# Create Sculptors category and sculptors within the category
sculptors = Artist(style="Sculptor")
session.add(sculptors)
session.commit()

sculptor1 = Name(name="Michelangelo", description="Italian sculptor, painter, architect and poet of the High Renaissance",
                 artist=sculptors, user=user1)
session.add(sculptor1)
session.commit()

sculptor2 = Name(name="Donatello", description="Italian Renaissance sculptor who was an artist of the 15th century",
                 artist=sculptors)
session.add(sculptor2)
session.commit()
