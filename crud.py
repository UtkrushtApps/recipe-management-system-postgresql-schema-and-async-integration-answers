from sqlalchemy.future import select
from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from db import AsyncSessionLocal
from models import Recipe, Ingredient, Category, recipe_ingredient, AccessLog

async def create_category(session, name:str):
    cat = Category(name=name)
    session.add(cat)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        q = await session.execute(select(Category).where(func.lower(Category.name) == name.lower()))
        cat = q.scalar_one()
    return cat

async def get_category_by_name(session, name:str):
    q = await session.execute(select(Category).where(func.lower(Category.name) == name.lower()))
    return q.scalar_one_or_none()

async def get_ingredient(session, name:str):
    q = await session.execute(select(Ingredient).where(func.lower(Ingredient.name) == name.lower()))
    return q.scalar_one_or_none()

async def create_ingredient(session, name:str):
    ingr = Ingredient(name=name)
    session.add(ingr)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        q = await session.execute(select(Ingredient).where(func.lower(Ingredient.name) == name.lower()))
        ingr = q.scalar_one()
    return ingr

async def create_recipe(session, title:str, description:str, instructions:str, category_name:str, ingredient_names:list):
    category = await get_category_by_name(session, category_name)
    if not category:
        category = await create_category(session, category_name)
    ingredients = []
    for n in ingredient_names:
        ingr = await get_ingredient(session, n)
        if not ingr:
            ingr = await create_ingredient(session, n)
        ingredients.append(ingr)
    recipe = Recipe(title=title, description=description, instructions=instructions, category=category, ingredients=ingredients)
    session.add(recipe)
    await session.commit()
    await session.refresh(recipe)
    return recipe

async def get_recipe(session, recipe_id:int):
    q = await session.execute(
        select(Recipe).options(
            selectinload(Recipe.category),
            selectinload(Recipe.ingredients)
        ).where(Recipe.id == recipe_id)
    )
    return q.scalar_one_or_none()

async def search_recipes_by_ingredient(session, ingredient:str, offset:int=0, limit:int=20):
    # Uses indexed table join for efficiency.
    q = await session.execute(
        select(Recipe)
        .join(recipe_ingredient)
        .join(Ingredient)
        .options(selectinload(Recipe.category), selectinload(Recipe.ingredients))
        .where(func.lower(Ingredient.name) == ingredient.lower())
        .offset(offset)
        .limit(limit)
    )
    return q.scalars().all()

async def list_recipes_by_category(session, category:str, offset:int=0, limit:int=20):
    q = await session.execute(
        select(Recipe)
        .join(Category)
        .options(selectinload(Recipe.category), selectinload(Recipe.ingredients))
        .where(func.lower(Category.name) == category.lower())
        .offset(offset)
        .limit(limit)
    )
    return q.scalars().all()

async def search_recipes(session, query:str, offset:int=0, limit:int=20):
    """Search by title, description, or ingredient name, case-insensitive."""
    q = await session.execute(
        select(Recipe)
        .outerjoin(recipe_ingredient)
        .outerjoin(Ingredient)
        .options(selectinload(Recipe.category), selectinload(Recipe.ingredients))
        .where(
            or_(func.lower(Recipe.title).contains(query.lower()),
                func.lower(Recipe.description).contains(query.lower()),
                func.lower(Ingredient.name).contains(query.lower())
                )
        )
        .offset(offset).limit(limit)
    )
    return q.scalars().unique().all()

async def list_all_recipes(session, offset:int=0, limit:int=20):
    q = await session.execute(
        select(Recipe)
        .options(selectinload(Recipe.category), selectinload(Recipe.ingredients))
        .offset(offset)
        .limit(limit)
    )
    return q.scalars().all()

async def list_categories(session):
    q = await session.execute(select(Category))
    return q.scalars().all()

async def list_ingredients(session):
    q = await session.execute(select(Ingredient))
    return q.scalars().all()

async def log_access(session, endpoint:str, method:str, user_agent:str=None):
    log = AccessLog(endpoint=endpoint, method=method, user_agent=user_agent)
    session.add(log)
    await session.commit()
