var tab_slotow = [0, 0, 0]
const icon_width = 79 ,
      icon_height = 79 ,
      num_icons = 9 ,
      time_per_icon = 100,
      indexes = [0, 0, 0];
      iconMap = ["banana", "seven", "bar", "lemon", "cherry", "plum", "orange", "bell", "watermelon"]
const roll = (reel, offset = 0, back_rand) => {
    //console.log(back_rand);
    //const delta = (offset + 2) * num_icons + Math.round(Math.random() * num_icons);
    const delta = (offset + 2) * num_icons + back_rand;
    const style = getComputedStyle(reel),
        backgroundPositionY = parseFloat(style["background-position-y"]);

    reel.style.transition = `background-position-y ${8 + delta * time_per_icon}ms cubic-bezier(.45,.05,.58,1.09)`;
    reel.style.backgroundPositionY = `${backgroundPositionY + delta * icon_height}px`;
}
function rollAll(back_rand_list){
    const reelsList = document.querySelectorAll('.slots > .reel');
    [...reelsList].map((reel,i) => {
        roll(reel, i, back_rand_list[i]);
        tab_slotow[i]+=back_rand_list[i];
        tab_slotow[i]=tab_slotow[i] % 9;
        console.log(i, tab_slotow[i]);
    })
    return(true)
}