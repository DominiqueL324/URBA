function toggleDropdown () {
   
    // const dropdownMenu = document.getElementById('dropdown')
    // dropdownMenu.classList.toggle('is-active')

   
    // console.log(1)
}

document.addEventListener('click', function (e) {
    if (e.target.classList.contains('image-profile')) {
        let dropdownMenu = document.getElementById('dropdown')
        dropdownMenu.classList.toggle('is-active')
        console.log(e.target)
    } else {
        let dropdownMenu = document.getElementById('dropdown')
        if (dropdownMenu.classList.contains('is-active')) {
            dropdownMenu.classList.toggle('is-active')
        }
    }
})