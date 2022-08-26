#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from dataclasses import dataclass
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from markupsafe import Markup
from flask_migrate import Migrate
import sys


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
# COMPLETED IN THE CONFIG FILE

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String, nullable=False)
    website_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    #establish connection between SHOWS and Venues
    shows = db.relationship("Show", backref="venues", lazy=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Venue id={self.id} name={self.name} city={self.city} state={self.city}> \n"



class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    #establish connection to Artist and Venues model
    shows = db.relationship("Show", backref="artists", lazy=False, cascade="all, delete-orphan")


#SHOWS model 
class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Show id={self.id} artist_id={self.artist_id} venue_id={self.venue_id} start_time={self.start_time}"


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  #get all venue information from the database
  venue_data = Venue.query.distinct(Venue.state, Venue.city).all()
  data = []
  for venue in venue_data:
    data.append({
      'id': venue.id,
      'state': venue.state,
      'city': venue.city,
      'venues': [{
        'id': venue.id,
        'name': venue.name,
      }]
    })

  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.

    search_term = request.form['search_term']

    response = {}
    venues = list(Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all())
    response["count"] = len(venues)
    response["data"] = []

    for venue in venues:
        venue_data = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
        }
        response["data"].append(venue_data)

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

    

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  #get the current time
  current_time = datetime.now()
  # shows the venue in the database with the id of the venue
  venue = Venue.query.get(venue_id)  


  #get all upcoming shows from the database
  upcoming_shows_data = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time > current_time).all()
  #print(upcoming_shows_data)
  upcoming_shows =[]
  for show in upcoming_shows_data:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "start_time": show.start_time,
      "upcoming_shows_count ": len(upcoming_shows),
    })

  #get all past shows from the database
  past_shows_data = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time < current_time).all()
  #print(past_shows_data)
  past_shows = []
  for show in past_shows_data:
    past_shows.append({
      "artist_id": show.artist_id,
      "start_time": show.start_time,
      "past_shows_count": len(past_shows)
    })

    #TODO: please guide me how to capture the upcoming and past shows based on the current codebase
    #data = list(filter(lambda d: d['id'] == venue_id, venue))
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)

    try:  
          add_venue = Venue(
            name = form.name.data,
            city = form.city.data,
            address = form.address.data,
            phone =form.phone.data,
            genres =",".join(form.genres.data),
            facebook_link =form.facebook_link.data,
            image_link =form.image_link.data,
            website_link =form.website_link.data,
            seeking_description =form.seeking_description.data,
            seeking_talent =form.seeking_talent.data
          )
          db.session.add(add_venue)
          db.session.commit()
          # on successful db insert, flash success
          flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
              db.session.rollback()
              print(sys.exc_info())
              flash('An error occurred. Venue ' + add_venue.name + 'could not be listed.')

    finally:
              db.session.close()     

    return render_template('pages/home.html')



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  #delete the venue from the database using the venue id
  try:
    delete_venue = Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash("Venue " + delete_venue.name + " was deleted successfully!")
    
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash("Venue was not deleted successfully.")

  finally:
    db.session.close()
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist.id, Artist.name).all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
def search_artists():

    search_term = request.form['search_term']
    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()

    response = {
        "count": len(artists),
        "data": artists
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
# TODO: replace with real artist data from the artist table, using artist_id
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  #data = list(filter(lambda d: d['id'] == artist_id, artist))[0]
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= Artist.query.get(artist_id)
  form.genres.data = artist.genres.split(',')
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
  form = ArtistForm(request.form)

  if form.validate():
    try:
        artist = Artist.query.get(artist_id)

        artist.name = form.name.data
        artist.city=form.city.data
        artist.state=form.state.data
        artist.phone=form.phone.data
        artist.genres=",".join(form.genres.data) 
        artist.facebook_link=form.facebook_link.data
        artist.image_link=form.image_link.data
        artist.seeking_venue=form.seeking_venue.data
        artist.seeking_description=form.seeking_description.data
        artist.website_link=form.website_link.data

        db.session.add(artist)
        db.session.commit()
        flash("Artist " + artist.name + " was successfully edited!")
    except:
              db.session.rollback()
              print(sys.exc_info())
              flash("Artist was not edited successfully.")
    finally:
              db.session.close()
  else:
      flash("Artist was not edited successfully.")            

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_data = Venue.query.get(venue_id)
  form.genres.data = venue_data.genres.split(",") 
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)

  if form.validate():
        try:
            venue = Venue.query.get(venue_id)

            venue.name = form.name.data
            venue.city=form.city.data
            venue.state=form.state.data
            venue.address=form.address.data
            venue.phone=form.phone.data
            venue.genres=",".join(form.genres.data)
            venue.facebook_link=form.facebook_link.data
            venue.image_link=form.image_link.data
            venue.website_link=form.website_link.data
            venue.seeking_talent=form.seeking_talent.data
            venue.seeking_description=form.seeking_description.data

            db.session.add(venue)
            db.session.commit()

            flash("Venue " + form.name.data + " edited successfully")
    
        except Exception:
          db.session.rollback()
          print(sys.exc_info())
          flash("Venue was not edited successfully.")
        finally:
          db.session.close()
  else: 
    flash("Venue was not edited successfully.")

  return redirect(url_for('show_venue', venue_id=venue_id))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)

  if form.validate():
        try:
            add_artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=",".join(form.genres.data),
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
            )

            db.session.add(add_artist)
            db.session.commit();

            flash("Artist " + request.form["name"] + " was successfully listed!")

        except:
            db.session.rollback()
            flash("Artist was not successfully listed")
            print(sys.exc_info())

        finally:
            db.session.close()
  else:
        print(form.errors)
        flash("Artist was not successfully listed.")


  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
# TODO: replace with real venues data.
def shows():

  data = []
  show_data = Show.query.all()

  for show in show_data:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    
    data.append({
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "start_time": str(show.start_time)
    })

  return render_template('pages/shows.html', shows=data)



@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)

  if form.validate():
        try:
            new_show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )
            db.session.add(new_show)
            db.session.commit()
            flash('Show was successfully listed!')

        except:
            db.session.rollback()
            print(sys.exc_info())
            flash('Show was not successfully listed.')

        finally:
            db.session.close()
  else:
        print(form.errors)
        flash('Show was not successfully listed.')
  
  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
