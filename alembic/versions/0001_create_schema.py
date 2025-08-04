from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index('ix_categories_id', 'categories', ['id'], unique=False)
    op.create_index('ix_categories_name', 'categories', ['name'], unique=True)

    op.create_table('ingredients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index('ix_ingredients_id', 'ingredients', ['id'], unique=False)
    op.create_index('ix_ingredients_name', 'ingredients', ['name'], unique=True)

    op.create_table('recipes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_recipes_id', 'recipes', ['id'], unique=False)
    op.create_index('ix_recipes_title', 'recipes', ['title'], unique=False)
    op.create_index('ix_recipes_category_id', 'recipes', ['category_id'], unique=False)

    op.create_table('recipe_ingredient',
        sa.Column('recipe_id', sa.Integer(), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('recipe_id', 'ingredient_id'),
    )
    op.create_index('ix_recipe_ingredient_recipe_id', 'recipe_ingredient', ['recipe_id'])
    op.create_index('ix_recipe_ingredient_ingredient_id', 'recipe_ingredient', ['ingredient_id'])

    op.create_table('access_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('endpoint', sa.String(length=200), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('user_agent', sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_access_logs_id', 'access_logs', ['id'], unique=False)

def downgrade():
    op.drop_index('ix_access_logs_id', table_name='access_logs')
    op.drop_table('access_logs')
    op.drop_index('ix_recipe_ingredient_ingredient_id', table_name='recipe_ingredient')
    op.drop_index('ix_recipe_ingredient_recipe_id', table_name='recipe_ingredient')
    op.drop_table('recipe_ingredient')
    op.drop_index('ix_recipes_category_id', table_name='recipes')
    op.drop_index('ix_recipes_title', table_name='recipes')
    op.drop_index('ix_recipes_id', table_name='recipes')
    op.drop_table('recipes')
    op.drop_index('ix_ingredients_name', table_name='ingredients')
    op.drop_index('ix_ingredients_id', table_name='ingredients')
    op.drop_table('ingredients')
    op.drop_index('ix_categories_name', table_name='categories')
    op.drop_index('ix_categories_id', table_name='categories')
    op.drop_table('categories')
