import './CategoryBadge.css'

function CategoryBadge({ category, onRemove, small = false }) {
  return (
    <span
      className={`category-badge ${small ? 'small' : ''}`}
      style={{ backgroundColor: category.color + '20', borderColor: category.color }}
    >
      <span className="badge-dot" style={{ backgroundColor: category.color }} />
      <span className="badge-name">{category.name}</span>
      {onRemove && (
        <button
          className="badge-remove"
          onClick={(e) => {
            e.stopPropagation()
            onRemove(category.id)
          }}
          title="Remove category"
        >
          ×
        </button>
      )}
    </span>
  )
}

export default CategoryBadge
