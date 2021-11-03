import factory.fuzzy
from django.contrib.auth.models import User
from menus.models import Dish, Menu

USER_PASSWORD = 'password'  # nosec


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f'user-{n}')
    email = factory.Sequence(lambda n: f'user-{n}@example.com')
    password = factory.PostGenerationMethodCall('set_password', USER_PASSWORD)
    is_active = factory.Faker('pybool')

    class Meta:
        model = User
        django_get_or_create = ('username',)


class MenuFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText()
    description = factory.fuzzy.FuzzyText()

    class Meta:
        model = Menu


class DishFactory(factory.django.DjangoModelFactory):
    menu = factory.SubFactory(MenuFactory)
    name = factory.fuzzy.FuzzyText()
    description = factory.fuzzy.FuzzyText()
    price = factory.fuzzy.FuzzyDecimal(low=0.01, high=100)
    time_to_prepare = factory.fuzzy.FuzzyInteger(low=5, high=120)
    is_vegetarian = factory.fuzzy.FuzzyChoice(choices=(True, False))

    class Meta:
        model = Dish
