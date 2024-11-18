document.addEventListener('DOMContentLoaded', function() {
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const closeSidebar = document.getElementById('close-sidebar');
  const sidebar = document.getElementById('sidebar');
  const userMenuButton = document.getElementById('user-menu-button');
  const priceRange = document.getElementById('price-range');
  const priceValue = document.getElementById('price-value');
  const categoryCheckboxes = document.querySelectorAll('input[name="category"]');
  const productList = document.getElementById('product-list');

  sidebarToggle.addEventListener('click', function() {
    sidebar.classList.toggle('-translate-x-full');
  });

  closeSidebar.addEventListener('click', function() {
    sidebar.classList.add('-translate-x-full');
  });

  userMenuButton.addEventListener('click', function() {
    // Toggle user menu dropdown
    // You may want to implement this functionality
  });

  // Price range slider
  priceRange.addEventListener('input', function() {
    priceValue.textContent = '$' + this.value;
  });

  // Filter function
  function filterProducts() {
    const selectedCategories = Array.from(categoryCheckboxes)
      .filter(cb => cb.checked)
      .map(cb => cb.value);
    const maxPrice = priceRange.value;

    fetch(`/api/products/?categories=${selectedCategories.join(',')}&max_price=${maxPrice}`)
      .then(response => response.json())
      .then(data => {
        productList.innerHTML = data.map(product => `
          <div class="bg-white rounded-lg shadow-md overflow-hidden">
            <img src="${product.image}" alt="${product.name}" class="w-full h-48 object-cover">
            <div class="p-4">
              <h3 class="text-lg font-semibold mb-2">${product.name}</h3>
              <p class="text-sm text-gray-600 mb-4">${product.description}</p>
              <div class="flex items-center justify-between">
                <span class="text-lg font-bold">$${product.price}</span>
                <button class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Add to Cart</button>
              </div>
            </div>
          </div>
        `).join('');
      });
  }

  // Add event listeners for filters
  categoryCheckboxes.forEach(cb => cb.addEventListener('change', filterProducts));
  priceRange.addEventListener('change', filterProducts);

  // Initial filter
  filterProducts();
});