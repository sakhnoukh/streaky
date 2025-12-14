import './CategoryFilter.css'

function CategoryFilter({ categories, selectedCategory, onSelectCategory }) {
  return (
    <div className="category-filter">
      <button
        className={`filter-btn ${selectedCategory === null ? 'active' : ''}`}
        onClick={() => onSelectCategory(null)}
      >
        All Habits
      </button>
      {categories.map((category) => (
        <button
          key={category.id}
          className={`filter-btn ${selectedCategory === category.id ? 'active' : ''}`}
          onClick={() => onSelectCategory(category.id)}
          style={{
            '--category-color': category.color,
          }}
        >
          <span
            className="filter-color-dot"
            style={{ backgroundColor: category.color }}
          />
          {category.name}
        </button>
      ))}
    </div>
  )
}

export default CategoryFilter
