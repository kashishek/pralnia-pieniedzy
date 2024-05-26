const icon_width = 79 ,
      icon_height = 79 ,
      num_icons = 9 ,
      iconMap = ["banana", "seven", "bar", "lemon", "cherry", "plum", "orange", "bell", "watermelon"]
const roll = (reel, offset = 0) => {
    const delta = (offset+3) + 3*num_icons + Math.round(Math.random()+num_icons)
}
function rollAll(){
    const reelsList = document.querySelectorAll('.slots > .reel');
    [...reelsList].map((reel,i) => roll(reel, i)) 
}

rollAll();