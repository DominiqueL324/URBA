const toggleBtn = document.getElementById('toggleBtn')

toggleBtn.addEventListener('click', function (e) {
    const sideMenu = document.getElementById('sideMenu')
    const main = document.getElementById('main')
    if (!sideMenu.classList.contains('close')) {
        toggleBtn.classList.toggle('rotate')
        sideMenu.classList.toggle('close')
        main.classList.toggle('increase_size')
    } else {
        toggleBtn.classList.toggle('rotate')
        sideMenu.classList.toggle('close')
        main.classList.toggle('increase_size')
    }
    // if menu is open then close it
    console.log(e)
    // else open it
})

const toggleSmallMenu = document.getElementById('toggleSmallMenu')

toggleSmallMenu.addEventListener('click', function (e) {
    const sideMenus = document.getElementById('sideMenu')
    if(!sideMenus.classList.contains('tablet-side-bar-open')) {
        sideMenus.classList.toggle('tablet-side-bar-open')
    } else {
        sideMenus.classList.toggle('tablet-side-bar-open')
    }
})