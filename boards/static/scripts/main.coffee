console.log("Welcome to Boards!")

openSidebar = ->
    sidebar = document.getElementById("sidebar")
    sidebar.style.height = document.hei
    sidebar.style.animation = '' # inherit from css
    sidebar.style.visibility = 'visible'

closeSidebar = ->
    sidebar = document.getElementById("sidebar")
    sidebar.style.animation = 'none'
    sidebar.style.visibility = 'hidden'

window.addEventListener('load',
  (->
      sidebar = document.getElementById("sidebar")
      sidebarOpener = document.getElementById("sidebarOpen")
      document.body.onclick = (e) ->
          if e.target != sidebar && e.target != sidebarOpener
              closeSidebar()
  )
)