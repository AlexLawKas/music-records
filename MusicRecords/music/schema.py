import graphene
from graphene_django.types import DjangoObjectType, ObjectType

# Create a GraphQL type for the actor model
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


class PerformerInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()
    genre = graphene.String()

class RecordInput(graphene.InputObjectType):
    id = graphene.ID()
    title = graphene.String()
    performers = graphene.List(PerformerInput)
    year = graphene.Int()


class SongInput(graphene.InputObjectType):
    id = graphene.ID()
    title = graphene.String()
    performers = graphene.List(PerformerInput)
    records = graphene.List(RecordInput)
    year = graphene.Int()


class CreatePerformer(graphene.Mutation):
    class Arguments:
        input = PerformerInput(required=True)

    ok = graphene.Boolean()
    performer = graphene.Field(PerformerType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        performer_instance = Performer(name=input.name, genre=input.genre)
        performer_instance.save()
        return CreatePerformer(ok=ok, performer=performer_instance)


class UpdatePerformer(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PerformerInput(required=True)

    ok = graphene.Boolean()
    performer = graphene.Field(PerformerType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        performer_instance = Performer.objects.get(pk=id)
        if performer_instance:
            ok = True
            performer_instance.name = input.name
            performer_instance.save()
            return UpdatePerformer(ok=ok, performer=performer_instance)
        return UpdatePerformer(ok=ok, performer=None)


class CreateRecord(graphene.Mutation):
    class Arguments:
        input = RecordInput(required=True)

    ok = graphene.Boolean()
    record = graphene.Field(RecordType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        performers = []
        for performer_input in input.performers:
            performer = Performer.objects.get(pk=performer_input.id)
            if performer is None:
                return CreateRecord(ok=False, record=None)
            performers.append(performer)
        record_instance = Records(
            title=input.title,
            year=input.year
        )
        record_instance.save()
        record_instance.performer.set(performers)
        return CreateRecord(ok=ok, record=record_instance)


class UpdateRecord(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = RecordInput(required=True)

    ok = graphene.Boolean()
    record = graphene.Field(RecordType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        record_instance = Records.objects.get(pk=id)
        if record_instance:
            ok = True
            performers = []
            for performer_input in input.performers:
                performer = Performer.objects.get(pk=performer_input.id)
                if performer is None:
                    return UpdateRecord(ok=False, record=None)
                performers.append(performer)
            record_instance.title = input.title
            record_instance.year = input.year
            record_instance.save()
            record_instance.performer.set(performers)
            return UpdateRecord(ok=ok, record=record_instance)
        return UpdateRecord(ok=ok, record=None)


class CreateSong(graphene.Mutation):
    class Arguments:
        input = SongInput(required=True)

    ok = graphene.Boolean()
    song = graphene.Field(SongType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        records = []
        performers = []
        for record_input in input.records:
            record = Records.objects.get(pk=record_input.id)
            if record is None:
                return CreateSong(ok=False, song=None)
            records.append(record)
        for performer_input in input.performers:
            performer = Performer.objects.get(pk=performer_input.id)
            if performer is None:
                return CreateSong(ok=False, song=None)
            performers.append(performer)
        song_instance = Songs(
            title=input.title,
            year=input.year
        )
        song_instance.save()
        song_instance.performer.set(performers)
        song_instance.record.set(records)
        return CreateSong(ok=ok, song=song_instance)


class UpdateSong(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = RecordInput(required=True)

    ok = graphene.Boolean()
    song = graphene.Field(SongType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        song_instance = Songs.objects.get(pk=id)
        if song_instance:
            ok = True
            records = []
            for record_input in input.records:
                record = Records.objects.get(pk=record_input.id)
                if record is None:
                    return UpdateSong(ok=False, song=None)
                records.append(record)
            song_instance.title = input.title
            song_instance.year = input.year
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
