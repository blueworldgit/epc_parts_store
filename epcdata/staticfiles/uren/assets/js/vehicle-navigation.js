// Vehicle Brand Navigation JavaScript - Styled to match category menu
document.addEventListener('DOMContentLoaded', function() {
    const vehicleBrandToggles = document.querySelectorAll('.vehicle-brand-toggle');
    
    vehicleBrandToggles.forEach(function(toggle) {
        const dropdown = toggle.closest('.vehicle-brand-dropdown');
        const dropdownContent = dropdown.querySelector('.vehicle-dropdown-content');
        let isOpen = false;
        let hideTimeout;
        
        // Function to show dropdown
        function showDropdown() {
            clearTimeout(hideTimeout);
            dropdownContent.style.display = 'block';
            setTimeout(function() {
                dropdownContent.classList.add('show');
                toggle.classList.add('active');
            }, 10);
            isOpen = true;
        }
        
        // Function to hide dropdown
        function hideDropdown() {
            dropdownContent.classList.remove('show');
            toggle.classList.remove('active');
            hideTimeout = setTimeout(function() {
                dropdownContent.style.display = 'none';
                isOpen = false;
            }, 300);
        }
        
        // Toggle on click (like category menu)
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Close all other dropdowns
            vehicleBrandToggles.forEach(function(otherToggle) {
                if (otherToggle !== toggle) {
                    const otherDropdown = otherToggle.closest('.vehicle-brand-dropdown');
                    const otherContent = otherDropdown.querySelector('.vehicle-dropdown-content');
                    otherContent.classList.remove('show');
                    otherToggle.classList.remove('active');
                    setTimeout(function() {
                        otherContent.style.display = 'none';
                    }, 300);
                }
            });
            
            // Toggle current dropdown
            if (isOpen) {
                hideDropdown();
            } else {
                showDropdown();
            }
        });
        
        // Show on hover (like category menu)
        dropdown.addEventListener('mouseenter', function() {
            showDropdown();
        });
        
        // Hide on mouse leave (with delay)
        dropdown.addEventListener('mouseleave', function() {
            hideDropdown();
        });
        
        // Keep dropdown open when hovering over content
        dropdownContent.addEventListener('mouseenter', function() {
            clearTimeout(hideTimeout);
        });
        
        dropdownContent.addEventListener('mouseleave', function() {
            hideDropdown();
        });
        
        // Prevent dropdown from closing when clicking inside it
        dropdownContent.addEventListener('click', function(e) {
            e.stopPropagation();
        });
        
        // Handle mega menu hover (for future parent categories)
        const megaMenuItems = dropdownContent.querySelectorAll('li.right-menu');
        megaMenuItems.forEach(function(item) {
            const megaMenu = item.querySelector('.vehicle-mega-menu');
            if (megaMenu) {
                item.addEventListener('mouseenter', function() {
                    megaMenu.style.opacity = '1';
                    megaMenu.style.visibility = 'visible';
                });
                
                item.addEventListener('mouseleave', function() {
                    megaMenu.style.opacity = '0';
                    megaMenu.style.visibility = 'hidden';
                });
            }
        });
    });
    
    // Close all dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.vehicle-brand-dropdown')) {
            vehicleBrandToggles.forEach(function(toggle) {
                const dropdown = toggle.closest('.vehicle-brand-dropdown');
                const dropdownContent = dropdown.querySelector('.vehicle-dropdown-content');
                dropdownContent.classList.remove('show');
                toggle.classList.remove('active');
                setTimeout(function() {
                    dropdownContent.style.display = 'none';
                }, 300);
            });
        }
    });
    
    // Add keyboard support (like category menu)
    vehicleBrandToggles.forEach(function(toggle) {
        toggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggle.click();
            }
        });
    });
});
