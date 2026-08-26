const app = {
    data: {
        ingredients: [],
        recipes: [],
        currentPlanUser: 'Carlos',
        recipeFormIngredients: []
    },

    init() {
        this.navigate('dashboard');
        this.fetchStats();
    },

    navigate(viewId, btnElement = null) {
        // Handle views
        document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
        document.getElementById(`view-${viewId}`).classList.add('active');

        // Handle sidebar nav active states
        if (btnElement) {
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
            btnElement.classList.add('active');
        }

        // Trigger specific loads based on view
        if (viewId === 'dashboard') this.fetchStats();
        if (viewId === 'ingredients') this.fetchIngredients();
        if (viewId === 'recipes') {
            this.fetchIngredients(); // needed for select
            this.fetchRecipes();
        }
        if (viewId === 'plan') {
            this.fetchRecipes(); // needed for selects
            this.renderPlan();
        }
        if (viewId === 'shopping') this.fetchShoppingList();
    },

    async fetchIngredients() {
        const res = await fetch('/api/ingredients');
        this.data.ingredients = await res.json();
        this.renderIngredients();
        this.renderIngredientSelect();
    },

    renderIngredients() {
        const list = document.getElementById('ingredients-list');
        list.innerHTML = '';
        this.data.ingredients.forEach(ing => {
            const li = document.createElement('li');
            li.textContent = ing.name;
            list.appendChild(li);
        });
    },

    async saveIngredient() {
        const nameInput = document.getElementById('new-ingredient-name');
        const name = nameInput.value.trim();
        if (!name) return;

        const res = await fetch('/api/ingredients', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name})
        });

        if (res.ok) {
            nameInput.value = '';
            this.fetchIngredients();
        } else {
            alert('Error al guardar ingrediente');
        }
    },

    renderIngredientSelect() {
        const select = document.getElementById('recipe-ing-select');
        if (!select) return;
        select.innerHTML = '<option value="">Selecciona ingrediente...</option>';
        this.data.ingredients.forEach(ing => {
            const opt = document.createElement('option');
            opt.value = ing.id;
            opt.textContent = ing.name;
            select.appendChild(opt);
        });
    },

    addIngredientToForm() {
        const select = document.getElementById('recipe-ing-select');
        const amount = document.getElementById('recipe-ing-amount').value.trim();
        const ingId = select.value;
        const ingName = select.options[select.selectedIndex]?.text;

        if (!ingId) return;

        this.data.recipeFormIngredients.push({
            ingredient_id: parseInt(ingId),
            name: ingName,
            amount: amount
        });

        this.renderRecipeFormIngredients();
        select.value = '';
        document.getElementById('recipe-ing-amount').value = '';
    },

    renderRecipeFormIngredients() {
        const list = document.getElementById('recipe-ing-list');
        list.innerHTML = '';
        this.data.recipeFormIngredients.forEach((ing, index) => {
            const li = document.createElement('li');
            li.textContent = `${ing.name} - ${ing.amount}`;
            const btn = document.createElement('button');
            btn.textContent = 'x';
            btn.style.marginLeft = '10px';
            btn.onclick = () => {
                this.data.recipeFormIngredients.splice(index, 1);
                this.renderRecipeFormIngredients();
            };
            li.appendChild(btn);
            list.appendChild(li);
        });
    },

    async saveRecipe() {
        const name = document.getElementById('recipe-name').value.trim();
        const instructions = document.getElementById('recipe-instructions').value.trim();

        if (!name) return alert('El nombre es obligatorio');

        const payload = {
            name,
            instructions,
            ingredients: this.data.recipeFormIngredients
        };

        const res = await fetch('/api/recipes', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            document.getElementById('recipe-name').value = '';
            document.getElementById('recipe-instructions').value = '';
            this.data.recipeFormIngredients = [];
            this.renderRecipeFormIngredients();
            this.fetchRecipes();
        } else {
            alert('Error al guardar receta');
        }
    },

    async fetchRecipes() {
        const res = await fetch('/api/recipes');
        this.data.recipes = await res.json();
        this.renderRecipes();
    },

    renderRecipes() {
        const container = document.getElementById('recipes-list');
        if (!container) return;
        container.innerHTML = '';

        this.data.recipes.forEach(recipe => {
            const card = document.createElement('div');
            card.className = 'card recipe-card';

            let ingsHtml = recipe.ingredients.map(i => `<li>${i.name}: ${i.amount}</li>`).join('');

            card.innerHTML = `
                <h3>${recipe.name}</h3>
                <p><strong>Instrucciones:</strong> ${recipe.instructions || 'N/A'}</p>
                <p><strong>Ingredientes:</strong></p>
                <ul>${ingsHtml}</ul>
            `;
            container.appendChild(card);
        });
    },

    async fetchStats() {
        const res = await fetch('/api/stats');
        const stats = await res.json();

        document.getElementById('stat-carlos-plan').textContent = stats.carlos_plan;
        document.getElementById('stat-almu-plan').textContent = stats.almu_plan;

        const recTop = document.getElementById('stat-recipes-top');
        if (recTop) recTop.textContent = stats.recipes;

        const ingTop = document.getElementById('stat-ingredients-top');
        if (ingTop) ingTop.textContent = stats.ingredients;

        const shopTop = document.getElementById('stat-shopping-top');
        if (shopTop) shopTop.textContent = stats.shopping_items;
    },

    async renderPlan() {
        const user = document.querySelector('input[name="plan-user"]:checked').value;
        const res = await fetch(`/api/plan?user=${user}`);
        const planData = await res.json();

        const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
        const meals = ['Desayuno', 'Comida', 'Cena'];

        const grid = document.getElementById('plan-grid');
        grid.innerHTML = '';

        days.forEach(day => {
            const card = document.createElement('div');
            card.className = 'plan-day-card';

            const title = document.createElement('h3');
            title.className = 'plan-day-title';
            title.textContent = day;
            card.appendChild(title);

            meals.forEach(meal => {
                const slot = document.createElement('div');
                slot.className = 'meal-slot';

                const label = document.createElement('span');
                label.className = 'meal-label';
                label.textContent = meal;
                slot.appendChild(label);

                // Find if there's a recipe assigned
                const assigned = planData.find(p => p.day === day && p.meal === meal);

                const select = document.createElement('select');
                select.className = 'input-select';
                select.innerHTML = '<option value="">- Vacío -</option>';

                this.data.recipes.forEach(r => {
                    const opt = document.createElement('option');
                    opt.value = r.id;
                    opt.textContent = r.name;
                    if (assigned && assigned.recipe_id === r.id) {
                        opt.selected = true;
                    }
                    select.appendChild(opt);
                });

                select.onchange = (e) => this.updatePlan(user, day, meal, e.target.value);

                slot.appendChild(select);
                card.appendChild(slot);
            });

            grid.appendChild(card);
        });
    },

    async updatePlan(user, day, meal, recipeId) {
        const payload = {
            user, day, meal,
            recipe_id: recipeId ? parseInt(recipeId) : null
        };

        await fetch('/api/plan', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
    },

    async fetchShoppingList() {
        const res = await fetch('/api/shopping_list');
        const items = await res.json();
        const list = document.getElementById('shopping-list');
        list.innerHTML = '';

        items.forEach(item => {
            const li = document.createElement('li');
            if (item.bought) li.classList.add('bought');

            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.checked = item.bought;
            cb.onchange = (e) => this.toggleShoppingItem(item.id, e.target.checked);

            li.appendChild(cb);
            li.appendChild(document.createTextNode(`${item.ingredient_name} - ${item.amount}`));

            list.appendChild(li);
        });
    },

    async toggleShoppingItem(id, bought) {
        await fetch('/api/shopping_list/toggle', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({id, bought: bought ? 1 : 0})
        });
        this.fetchShoppingList();
    },

    async generateShoppingList() {
        if (!confirm('¿Seguro que quieres sobreescribir la lista actual?')) return;
        await fetch('/api/shopping_list/generate', { method: 'POST' });
        this.fetchShoppingList();
    }
};

window.onload = () => app.init();
