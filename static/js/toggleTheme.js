if (sessionStorage.getItem('color-theme') === 'dark' || (!('color-theme' in sessionStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark')
}

var themeToggleBtn = document.getElementById('theme-toggle');

themeToggleBtn.addEventListener('click', function(){
    if (sessionStorage.getItem('color-theme')) {
        if (sessionStorage.getItem('color-theme') === 'light') {
            document.documentElement.classList.add('dark');
            sessionStorage.setItem('color-theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            sessionStorage.setItem('color-theme', 'light');
        }
    }else{
        if (document.documentElement.classList.contains('dark')) {
            document.documentElement.classList.remove('dark');
            sessionStorage.setItem('color-theme', 'light');
        } else {
            document.documentElement.classList.add('dark');
            sessionStorage.setItem('color-theme', 'dark');
        }
    }
}
)