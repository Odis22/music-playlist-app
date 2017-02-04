from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Playlist, Base, PlaylistSong, User

engine = create_engine('sqlite:///musicplaylist.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

User1 = User(name="Triple H", email="HHH@WWE.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

User2 = User(name="The Rock", email="Rock@WWE.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User2)
session.commit()

User3 = User(name="Triple A", email="AAA@WWE.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User3)
session.commit()

User4 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User4)
session.commit()


# Uplifting happy go luck music playlist
playlist1 = Playlist(name="Uplifting songs", user_id=1,)

session.add(playlist1)
session.commit()

playlistSong1 = PlaylistSong(name="Rise up", artist="Andra Day",
                      genre="pop", playlist=playlist1)

session.add(playlistSong1)
session.commit()


playlistSong2 = PlaylistSong(name="Stronger", artist="Kelly Clarkson",
                      genre="pop", playlist=playlist1)

session.add(playlistSong2)
session.commit()

playlistSong3 = PlaylistSong(name="ain't no mountain high enough", artist="Marvin Gaye and tammi terrell",
                      genre="RnB", playlist=playlist1)

session.add(playlistSong3)
session.commit()

playlistSong4 = PlaylistSong(name="Your love keeps lifting me higher", artist="jackie wilson",
                      genre="RnB", playlist=playlist1)

session.add(playlistSong4)
session.commit()

playlistSong5 = PlaylistSong(name="Roar", artist="Katy Perry",
                      genre="Pop", playlist=playlist1)

session.add(playlistSong5)
session.commit()

playlistSong6 = PlaylistSong(name="Happy", artist="Pharrell",
                      genre="Pop", playlist=playlist1)

session.add(playlistSong6)
session.commit()

# Romantic music playlist
playlist2 = Playlist(name="Romantic music", user_id=2)

session.add(playlist2)
session.commit()

playlistSong1 = PlaylistSong(name="Won't go home without you", artist="Maroon 5",
                      genre="pop", playlist=playlist2)

session.add(playlistSong1)
session.commit()


playlistSong2 = PlaylistSong(name="Stronger", artist="Kelly Clarkson",
                      genre="pop", playlist=playlist2)

session.add(playlistSong2)
session.commit()

playlistSong3 = PlaylistSong(name="My heart will go on", artist="Celine Dion",
                      genre="pop", playlist=playlist2)

session.add(playlistSong3)
session.commit()

playlistSong4 = PlaylistSong(name="I will always love you", artist="Whitney Houston",
                      genre="RnB", playlist=playlist2)

session.add(playlistSong4)
session.commit()

# angry workout playlist
playlist3 = Playlist(name="Angry Workout", user_id=3)

session.add(playlist2)
session.commit()

playlistSong1 = PlaylistSong(name="real n***** roll call", artist="Lil Jon and Ice cube",
                      genre="rap", playlist=playlist3)

session.add(playlistSong1)
session.commit()


playlistSong2 = PlaylistSong(name="Voices", artist="Rev theory",
                      genre="rock", playlist=playlist3)

session.add(playlistSong2)
session.commit()

playlistSong3 = PlaylistSong(name="Party boyz", artist="Shop Boyz",
                      genre="rap", playlist=playlist3)

session.add(playlistSong3)
session.commit()

playlistSong4 = PlaylistSong(name="No love", artist="Eminem",
                      genre="rap", playlist=playlist3)

session.add(playlistSong4)
session.commit()

# dance songs
playlist4 = Playlist(name="Dance songs", user_id=4)

session.add(playlist4)
session.commit()

playlistSong1 = PlaylistSong(name="rock your body", artist="Justin Timberlake",
                      genre="pop", playlist=playlist4)

session.add(playlistSong1)
session.commit()

playlistSong2 = PlaylistSong(name="All about that bass", artist="Megan Trainor",
                      genre="pop", playlist=playlist4)
					 
session.add(playlistSong2)
session.commit()

print "added new song to playlist"
