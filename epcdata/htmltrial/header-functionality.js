/**
 * Header functionality for Maxus Parts Direct
 * Matches parent site behavior
 */

(function() {
    'use strict';

    // Search functionality
    function toggleSearch() {
        const searchOverlay = document.querySelector('.tf_search_form');
        const searchForm = document.querySelector('#searchform');
        
        if (!searchOverlay || !searchForm) return;
        
        if (searchOverlay.classList.contains('tf_search_overlay_open')) {
            searchOverlay.classList.remove('tf_search_overlay_open');
            searchForm.classList.add('tf_hide');
        } else {
            searchOverlay.classList.add('tf_search_overlay_open');
            searchForm.classList.remove('tf_hide');
            // Focus on search input
            const searchInput = document.querySelector('#s');
            if (searchInput) {
                setTimeout(() => searchInput.focus(), 100);
            }
        }
    }

    // Mobile menu functionality
    function initMobileMenu() {
        const menuIcon = document.getElementById('menu-icon');
        const menuClose = document.getElementById('menu-icon-close');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (menuIcon && mobileMenu) {
            menuIcon.addEventListener('click', function(e) {
                e.preventDefault();
                mobileMenu.classList.remove('sidemenu-off');
                mobileMenu.classList.add('sidemenu-on');
                document.body.style.overflow = 'hidden'; // Prevent body scroll
            });
        }
        
        if (menuClose && mobileMenu) {
            menuClose.addEventListener('click', function(e) {
                e.preventDefault();
                mobileMenu.classList.remove('sidemenu-on');
                mobileMenu.classList.add('sidemenu-off');
                document.body.style.overflow = ''; // Restore body scroll
            });
        }
    }

    // Cart slide functionality
    function initCartSlide() {
        const cartIcons = document.querySelectorAll('.cart-icon-link');
        const cartClose = document.getElementById('cart-icon-close');
        const slideCart = document.getElementById('slide-cart');
        
        cartIcons.forEach(function(cartIcon) {
            cartIcon.addEventListener('click', function(e) {
                // Only prevent default if it's a slide cart trigger, not actual cart link
                if (cartIcon.getAttribute('href') === '#slide-cart') {
                    e.preventDefault();
                    if (slideCart) {
                        slideCart.classList.remove('sidemenu-off');
                        slideCart.classList.add('sidemenu-on');
                        document.body.style.overflow = 'hidden';
                    }
                }
            });
        });
        
        if (cartClose && slideCart) {
            cartClose.addEventListener('click', function(e) {
                e.preventDefault();
                slideCart.classList.remove('sidemenu-on');
                slideCart.classList.add('sidemenu-off');
                document.body.style.overflow = '';
            });
        }
    }

    // Search button functionality
    function initSearchButton() {
        const searchButtons = document.querySelectorAll('.search-button, .tf_search_icon');
        
        searchButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                toggleSearch();
            });
        });

        // Close search on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const searchOverlay = document.querySelector('.tf_search_form');
                const searchForm = document.querySelector('#searchform');
                
                if (searchOverlay && searchOverlay.classList.contains('tf_search_overlay_open')) {
                    searchOverlay.classList.remove('tf_search_overlay_open');
                    if (searchForm) {
                        searchForm.classList.add('tf_hide');
                    }
                }
            }
        });

        // Close search when clicking on overlay
        const searchOverlay = document.querySelector('.tf_search_form');
        if (searchOverlay) {
            searchOverlay.addEventListener('click', function(e) {
                if (e.target === searchOverlay) {
                    toggleSearch();
                }
            });
        }
    }

    // Fixed header functionality
    function initFixedHeader() {
        const headerWrap = document.getElementById('headerwrap');
        if (!headerWrap) return;

        let lastScrollY = window.scrollY;
        let ticking = false;

        function updateHeader() {
            const scrollY = window.scrollY;
            
            if (scrollY > 100) {
                headerWrap.classList.add('fixed-header');
            } else {
                headerWrap.classList.remove('fixed-header');
            }
            
            lastScrollY = scrollY;
            ticking = false;
        }

        function requestTick() {
            if (!ticking) {
                requestAnimationFrame(updateHeader);
                ticking = true;
            }
        }

        window.addEventListener('scroll', requestTick);
    }

    // Basket quantity update (for Django Oscar integration)
    function updateBasketQuantity() {
        // This would be called after adding items to basket
        // You can integrate with Django Oscar's basket update events
        const quantityElements = document.querySelectorAll('.cart-count');
        
        // This is a placeholder - integrate with your basket system
        fetch('/api/basket/quantity/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            quantityElements.forEach(element => {
                element.textContent = data.quantity || '0';
                element.style.display = data.quantity > 0 ? 'block' : 'none';
            });
        })
        .catch(error => {
            console.log('Could not update basket quantity:', error);
        });
    }

    // Get CSRF token for Django
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Initialize everything when DOM is loaded
    function init() {
        initMobileMenu();
        initCartSlide();
        initSearchButton();
        initFixedHeader();
        
        // Update basket quantity on page load
        updateBasketQuantity();
        
        // Listen for basket update events (customize based on your Oscar setup)
        document.addEventListener('basket-updated', updateBasketQuantity);
    }

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose toggleSearch globally for onclick handlers
    window.toggleSearch = toggleSearch;
    window.updateBasketQuantity = updateBasketQuantity;

})();
