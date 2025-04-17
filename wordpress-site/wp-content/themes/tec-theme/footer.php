    <footer class="site-footer">
        <div class="footer-content">
            <div class="footer-navigation">
                <?php
                wp_nav_menu(array(
                    'theme_location' => 'footer',
                    'menu_id'        => 'footer-menu',
                    'fallback_cb'    => false,
                ));
                ?>
            </div>
            
            <div class="site-info">
                <p>&copy; <?php echo date('Y'); ?> <?php bloginfo('name'); ?>. Powered by AIRTH.</p>
            </div>
        </div>
    </footer>

    <?php wp_footer(); ?>
</body>
</html>