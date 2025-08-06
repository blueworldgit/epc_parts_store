// Vehicle Brand Navigation JavaScript
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
            }, 10);
            isOpen = true;
        }
        
        // Function to hide dropdown
        function hideDropdown() {
            dropdownContent.classList.remove('show');
            hideTimeout = setTimeout(function() {
                dropdownContent.style.display = 'none';
                isOpen = false;
            }, 300);
        }
        
        // Toggle on click
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Close all other dropdowns
            vehicleBrandToggles.forEach(function(otherToggle) {
                if (otherToggle !== toggle) {
                    const otherDropdown = otherToggle.closest('.vehicle-brand-dropdown');
                    const otherContent = otherDropdown.querySelector('.vehicle-dropdown-content');
                    otherContent.classList.remove('show');
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
        
        // Show on hover
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
    });
    
    // Close all dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.vehicle-brand-dropdown')) {
            vehicleBrandToggles.forEach(function(toggle) {
                const dropdown = toggle.closest('.vehicle-brand-dropdown');
                const dropdownContent = dropdown.querySelector('.vehicle-dropdown-content');
                dropdownContent.classList.remove('show');
                setTimeout(function() {
                    dropdownContent.style.display = 'none';
                }, 300);
            });
        }
    });
});
