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
    performers = graphene.List(PerformerType)
    records = graphene.List(RecordType)
    songs = graphene.List(SongType)

    def resolve_performer(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Performer.objects.get(pk=id)

        return None

    def resolve_record(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Records.objects.get(pk=id)

    def resolve_song(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Songs.objects.get(pk=id)

        return None

    def resolve_performers(self, info, **kwargs):
        return Performer.objects.all()

    def resolve_records(self, info, **kwargs):
        return Records.objects.all()

    def resolve_songs(self, info, **kwargs):
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
    performers = graphene.List(PerformerParams)
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
        ok = False
        errors = []
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

    @staticmethod
    def mutate(root, info, params=None):
        ok = True
        records = []
        performers = []
        for record_params in params.records:
            record = Records.objects.get(pk=record_params.id)
            if record is None:
                return CreateSong(ok=False, song=None)
            records.append(record)
        for performer_params in params.performers:
            performer = Performer.objects.get(pk=performer_params.id)
            if performer is None:
                return CreateSong(ok=False, song=None)
            performers.append(performer)
        song_instance = Songs(
            title=params.title,
            year=params.year
        )
        song_instance.save()
        song_instance.performer.set(performers)
        song_instance.record.set(records)
        return CreateSong(ok=ok, song=song_instance)


class UpdateSong(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        params = RecordParams(required=True)

    ok = graphene.Boolean()
    song = graphene.Field(SongType)

    @staticmethod
    def mutate(root, info, id, params=None):
        ok = False
        song_instance = Songs.objects.get(pk=id)
        if song_instance:
            ok = True
            records = []
            for record_params in params.records:
                record = Records.objects.get(pk=record_params.id)
                if record is None:
                    return UpdateSong(ok=False, song=None)
                records.append(record)
            song_instance.title = params.title
            song_instance.year = params.year
            song_instance.save()
            song_instance.record.set(records)
            return UpdateSong(ok=ok, song=song_instance)
        return UpdateSong(ok=ok, song=None)


class Mutation(graphene.ObjectType):
    create_performer = CreatePerformer.Field()
    update_performer = UpdatePerformer.Field()
    create_record = CreateRecord.Field()
    update_record = UpdateRecord.Field()
    create_song = CreateSong.Field()
    update_song = UpdateSong.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
