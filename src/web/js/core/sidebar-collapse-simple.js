/**
 * Simple Sidebar Collapse - Clean Implementation
 */

(function() {
    'use strict';
    
    console.log('[SIDEBAR] Simple collapse script loaded');
    
    // Wait for DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCollapse);
    } else {
        initCollapse();
    }
    
    function initCollapse() {
        console.log('[SIDEBAR] Initializing collapse functionality');
        
        // Get elements
        const sidebar = document.getElementById('sidebar');
        const toggleBtn = document.getElementById('toggleSidebarBtn');
        const toggleIcon = document.getElementById('toggleIcon');
        const mainContent = document.querySelector('.main-content');
        
        // Check if elements exist
        if (!sidebar) {
            console.error('[SIDEBAR] Sidebar not found!');
            return;
        }
        if (!toggleBtn) {
            console.error('[SIDEBAR] Toggle button not found!');
            return;
        }
        if (!mainContent) {
            console.error('[SIDEBAR] Main content not found!');
            return;
        }
        
        console.log('[SIDEBAR] All elements found successfully');
        console.log('[SIDEBAR] Initial sidebar width:', window.getComputedStyle(sidebar).width);
        
        // Load saved state
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            console.log('[SIDEBAR] Restoring collapsed state from localStorage');
            sidebar.classList.add('collapsed');
            if (toggleIcon) toggleIcon.textContent = '▶';
        }
        
        // Simple toggle function
        window.toggleSidebar = function() {
            console.log('[SIDEBAR] ==== TOGGLE CALLED ====');
            console.log('[SIDEBAR] Before - Has collapsed class:', sidebar.classList.contains('collapsed'));
            console.log('[SIDEBAR] Before - Width:', window.getComputedStyle(sidebar).width);
            
            // Toggle the class
            sidebar.classList.toggle('collapsed');
            
            const isCollapsed = sidebar.classList.contains('collapsed');
            
            console.log('[SIDEBAR] After - Has collapsed class:', isCollapsed);
            
            // Update icon
            if (toggleIcon) {
                toggleIcon.textContent = isCollapsed ? '▶' : '◀';
            }
            
            // Save state
            localStorage.setItem('sidebarCollapsed', isCollapsed);
            
            // Force layout recalculation
            setTimeout(() => {
                console.log('[SIDEBAR] Final width:', window.getComputedStyle(sidebar).width);
                console.log('[SIDEBAR] Main content margin:', window.getComputedStyle(mainContent).marginLeft);
            }, 400);
        };
        
        console.log('[SIDEBAR] Collapse functionality initialized successfully');
        console.log('[SIDEBAR] Try clicking the ◀ button at the bottom of sidebar');
    }
})();
