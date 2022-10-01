import graphene
from graphene_django.types import DjangoObjectType, ObjectType

# Create a GraphQL type for the actor model
from music.errors import empty_name, exist
from music.models import Performer, Records, Songs


class PerformerType(DjangoObjectType):
    class Meta:
        model = Performer
        # Create a GraphQL type for the movie model


class RecordType(DjangoObjectType):
    class Meta:
        model = Records


class SongType(DjangoObjectType):
    class Meta:
        model = Songs


class Query(ObjectType):
    performer = graphene.Field(PerformerType, id=graphene.Int())
    record = graphene.Field(RecordType, id=graphene.Int())
    song = graphene.Field(SongType, id=graphene.Int())
    performers = graphene.List(PerformerType, name=graphene.String(), genre=graphene.String())
    records = graphene.List(RecordType, title=graphene.String(), year=graphene.Int())
    songs = graphene.List(SongType, title=graphene.String(), year=graphene.Int())

    def resolve_performer(self, info, **kwargs):
        info = 'Исполнитель'
        id = kwargs.get('id')

        if id is not None:
            return Performer.objects.get(pk=id)

        return None

    def resolve_record(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Records.objects.get(pk=id)
        return None

    def resolve_song(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Songs.objects.get(pk=id)

        return None

    def resolve_performers(self, info, **kwargs):
        name = kwargs.get('name')
        genre = kwargs.get('genre')
        if name is not None and genre is None:
            return Performer.objects.filter(name=name)
        elif genre is not None and name is None:
            return Performer.objects.filter(genre=genre)
        elif name is not None and genre is not None:
            return Performer.objects.filter(name=name, genre=genre)
        return Performer.objects.all()

    def resolve_records(self, info, **kwargs):
        title = kwargs.get('title')
        year = kwargs.get('year')
        if title is not None and year is None:
            return Records.objects.filter(title=title)
        elif year is not None and title is None:
            return Records.objects.filter(year=year)
        elif title is not None and year is not None:
            return Records.objects.filter(title=title, year=year)
        return Records.objects.all()

    def resolve_songs(self, info, **kwargs):
        title = kwargs.get('title')
        year = kwargs.get('year')
        if title is not None and year is None:
            return Songs.objects.filter(title=title)
        elif year is not None and title is None:
            return Songs.objects.filter(year=year)
        elif title is not None and year is not None:
            return Songs.objects.filter(title=title, year=year)
        return Songs.objects.all()



class PerformerParams(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()
    genre = graphene.String()


class RecordParams(graphene.InputObjectType):
    id = graphene.ID()
    title = graphene.String()
    performer = graphene.Int()
    year = graphene.Int()
    image = graphene.String()


class SongParams(graphene.InputObjectType):
    id = graphene.ID()
    title = graphene.String()
    performer = graphene.Int()
    records = graphene.List(RecordParams)
    year = graphene.Int()


class CreatePerformer(graphene.Mutation):
    class Arguments:
        params = PerformerParams(required=True)

    ok = graphene.Boolean()
    performer = graphene.Field(PerformerType)
    errors = graphene.List(graphene.String, required=True)

    @staticmethod
    def mutate(root, info, params=None):
        errors = []
        ok = False
        if not params.name:
            errors.append(f'Название {empty_name}')
        if Performer.objects.filter(name=params.name).exists():
            errors.append(f'Исполнитель с таким названием {params.name} {exist}')
        if not errors:
            ok = True
            performer_instance = Performer(name=params.name, genre=params.genre)
            performer_instance.save()
            return CreatePerformer(ok=ok, errors=errors, performer=performer_instance)
        return CreatePerformer(errors=errors, ok=ok, performer=None)


class UpdatePerformer(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        params = PerformerParams(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String, required=True)
    performer = graphene.Field(PerformerType)

    @staticmethod
    def mutate(root, info, id, params=None):
        errors = []
        ok = False
        performer_exist = False
        performers = Performer.objects.all()
        if performers is None:
            errors.append(f'Исполнителя с id {id} не существует')
        else:
            for performer in performers:
                if performer.id == id:
                    performer_true = True

        if performer_exist is False:
            errors.append(f'Исполнителя с id {id} не существует')
            return UpdateSong(errors=errors, ok=ok, song=None)
        if not params.name:
            errors.append(f'{params.name} {empty_name}')
        if Performer.objects.filter(name=params.name).exclude(id=id).exists():
            errors.append(f'Исполнитель с таким названием {params.name} {exist}')
        performer_instance = Performer.objects.get(pk=id)
        if not errors:
            ok = True
            performer_instance.name = params.name
            performer_instance.genre = params.genre
            performer_instance.save()
            return UpdatePerformer(ok=ok, errors=errors, performer=performer_instance)
        else:
            return UpdatePerformer(errors=errors, performer=None)


class CreateRecord(graphene.Mutation):
    class Arguments:
        params = RecordParams(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String, required=True)
    record = graphene.Field(RecordType)

    @staticmethod
    def mutate(root, info, params=None):
        ok = False
        errors = []
        if Records.objects.filter(title=params.title, performer=params.performer).exists():
            errors.append(f'Альбом {params.title} уже есть у исполнителя с id {params.performer}')

        elif params.performer is None:
            errors.append(f'Исполнитель должен быть указан')

        elif not Performer.objects.filter(id=params.performer).exists():
            errors.append(f'Исполнитель с id {params.performer} не существует')

        if not errors:
            performer_obj = Performer.objects.filter(pk=params.performer).get()
            ok = True
            record_instance = Records(
                title=params.title,
                year=params.year,
                performer_id=performer_obj.id,
                image=params.image
            )
            record_instance.save()
            return CreateRecord(ok=ok, errors=errors, record=record_instance)
        else:
            return CreateRecord(errors=errors, ok=ok, record=None)


class UpdateRecord(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        params = RecordParams(required=True)

    ok = graphene.Boolean()
    record = graphene.Field(RecordType)
    errors = graphene.List(graphene.String, required=True)

    @staticmethod
    def mutate(root, info, id, params=None):
        ok = False
        errors = []
        record_exist = False
        records = Records.objects.all()
        if records is None:
            errors.append(f'Альбома с id {id} не существует')
        else:
            for record in records:
                if record.id == id:
                    record_true = True

        if record_exist is False:
            errors.append(f'Песни с id {id} не существует')
            return UpdateSong(errors=errors, ok=ok, song=None)
        if Records.objects.filter(title=params.title, performer=params.performer).exclude(id=id).exists():
            errors.append(f'Альбом {params.title} уже есть у исполнителя с id {params.performer}')

        elif params.performer is None:
            errors.append(f'Исполнитель должен быть указан')

        elif not Performer.objects.filter(id=params.performer).exists():
            errors.append(f'Исполнитель с id {params.performer} не существует')

        if not errors:
            record_instance = Records.objects.get(pk=id)
            performer_obj = Performer.objects.filter(pk=params.performer).get()
            ok = True
            record_instance.title = params.title
            record_instance.year = params.year
            record_instance.performer_id = performer_obj.id
            record_instance.image = params.image

            record_instance.save()
            return UpdateRecord(ok=ok, errors=errors, record=record_instance)
        else:
            return UpdateRecord(errors=errors, ok=ok, record=None)


class CreateSong(graphene.Mutation):
    class Arguments:
        params = SongParams(required=True)

    ok = graphene.Boolean()
    song = graphene.Field(SongType)
    errors = graphene.List(graphene.String, required=True)

    @staticmethod
    def mutate(root, info, params=None):
        ok = False
        errors = []
        records = []
        if params.performer is None:
            errors.append(f'Исполнитель должен быть указан')
        elif not Performer.objects.filter(id=params.performer).exists():
            errors.append(f'Исполнитель с id {params.performer} не существует')
        if params.records is not None:
            for record_params in params.records:
                if not Records.objects.filter(id=record_params.id).exists():
                    errors.append(f'Альбом с id {record_params} не существует')
        if Songs.objects.filter(title=params.title, performer=params.performer).exists():
            errors.append(f'Песня {params.title} уже есть у исполнителя с id {params.performer}')
        if not errors:
            performer_obj = Performer.objects.filter(pk=params.performer).get()
            if params.records is not None:

                for record_params in params.records:
                    record = Records.objects.get(pk=record_params.id)
                    records.append(record)
            ok = True
            song_instance = Songs(
                title=params.title,
                year=params.year,
                performer_id=performer_obj.id,

            )
            song_instance.save()
            song_instance.records.set(records)

            return CreateSong(ok=ok, errors=errors, song=song_instance)
        else:
            return CreateSong(errors=errors, ok=ok, song=None)


class UpdateSong(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        params = SongParams(required=True)

    ok = graphene.Boolean()
    song = graphene.Field(SongType)
    errors = graphene.List(graphene.String, required=True)

    @staticmethod
    def mutate(root, info, id, params=None):
        ok = False
        errors = []
        song_exist = False
        songs = Songs.objects.all()
        if songs is None:
            errors.append(f'Песни с id {id} не существует')
        else:
            for song in songs:
                if song.id == id:
                    song_true = True

        if song_exist is False:
            errors.append(f'Песни с id {id} не существует')
            return UpdateSong(errors=errors, ok=ok, song=None)
        song_instance = Songs.objects.get(pk=id)
        if song_instance:
            ok = False
            errors = []
            records = []
            if params.performer is None:
                errors.append(f'Исполнитель должен быть указан')
            elif not Performer.objects.filter(id=params.performer).exists():
                errors.append(f'Исполнитель с id {params.performer} не существует')
            if params.records is not None:
                for record_params in params.records:
                    if not Records.objects.filter(id=record_params.id).exists():
                        errors.append(f'Альбом с id {record_params.id} не существует')
            if Songs.objects.filter(title=params.title, performer=params.performer).exclude(id=id).exists():
                errors.append(f'Песня {params.title} уже есть у исполнителя с id {params.performer}')
            if not errors:
                performer_obj = Performer.objects.filter(pk=params.performer).get()
                if params.records is not None:

                    for record_params in params.records:
                        record = Records.objects.get(pk=record_params.id)
                        records.append(record)
                ok = True
                song_instance.title = params.title
                song_instance.year = params.year
                song_instance.performer_id = performer_obj.id

                song_instance.save()
                song_instance.records.set(records)

                return UpdateSong(ok=ok, errors=errors, song=song_instance)
            else:
                return UpdateSong(errors=errors, ok=ok, song=None)


class Mutation(graphene.ObjectType):
    create_performer = CreatePerformer.Field()
    update_performer = UpdatePerformer.Field()
    create_record = CreateRecord.Field()
    update_record = UpdateRecord.Field()
    create_song = CreateSong.Field()
    update_song = UpdateSong.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
