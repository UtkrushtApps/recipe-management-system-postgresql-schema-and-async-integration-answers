from sqlalchemy import Column, Integer, String, ForeignKey, Text, Table, Index, DateTime, func
from sqlalchemy.orm import relationship
from db import Base

# Association table between Recipe and Ingredient
recipe_ingredient = Table(
    "recipe_ingredient",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True),
    Index("ix_recipe_ingredient_ingredient_id", "ingredient_id"),
    Index("ix_recipe_ingredient_recipe_id", "recipe_id")
)

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    instructions = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), index=True)
    
    category = relationship("Category", back_populates="recipes")
    ingredients = relationship("Ingredient", secondary=recipe_ingredient, back_populates="recipes")

    __table_args__ = (Index("ix_recipes_category_id", "category_id"),)

class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    recipes = relationship("Recipe", secondary=recipe_ingredient, back_populates="ingredients")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    
    recipes = relationship("Recipe", back_populates="category")

class AccessLog(Base):
    __tablename__ = "access_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    endpoint = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)
    user_agent = Column(String(200), nullable=True)