from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv
from os import environ
from marshmallow import post_load, fields, ValidationError

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Models
class MusicLibrary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(225), nullable=False)
    artist = db.Column(db.String(225), nullable=False)
    album = db.Column(db.Integer, nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    genre = db.Column(db.String(225), nullable=False)

    def __repr__(self):
        return f"{self.title}, {self.artist}, {self.album}, {self.release_date}, {self.genre}"
# Schemas
class SongSchema(ma.Schema):
    id = fields.Integer(primary_key=True)
    title = fields.String(required=True)
    artist = fields.String(required=True)
    album = fields.String(required=True)
    release_date = fields.Date(required=True)
    genre = fields.String(required=True)
    @post_load
    def create_song(self, data):
        return MusicLibrary(**data)
    
    class Meta:
        fields = "id", "title", "artist", "album", "release_date", "genre"

music_library = MusicLibrary()
music_librarys = MusicLibrary()
# Resources
class Music_Library_Resource(Resource):
      def get(self):
        all_music = SongSchema.query.all()
        return music_librarys.dump(all_music), 200
      

      def post(self):
        form_data = request.get_json()
        try:
            new_music = music_library.load(form_data)
            db.session.add(new_music)
            db.session.commit()
            db.session.dump(new_music), 201
        except ValidationError as err:
            return err.messages, 400
        
class MusicResource(Resource):
     def get(self, music_id):
        music_from_db = MusicLibrary.query.get_or_404(music_id)
        return music_library.dump(music_from_db)

     def delete(self, music_id):
        music_from_db = MusicLibrary.query.get_or_404(music_id)
        db.session.delete(music_from_db)
        return "", 204

     def put(self, music_id):
        music_from_db = MusicLibrary.query.get_or_404(music_id)
        if "title" in request.json:
            music_from_db.title = request.json['title']
        if "artist" in request.json:
            music_from_db.artist = request.json['artist']
        if "album" in request.json:
            music_from_db.album = request.json['album']
        if "release_date" in request.json:
            music_from_db.release_date = request.json['release_date']
        if "genre" in request.json:
            music_from_db.genre = request.json['genre']
        return "", 200




# Routes
api.add_resource(Music_Library_Resource,'api/songs')
api.add_resource(MusicResource, 'api/songs/<int:pk>')