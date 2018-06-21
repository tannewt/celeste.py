lifeup = {
    init=function(this)
        this.spd.y=-0.25
        this.duration=30
        this.x-=2
        this.y-=4
        this.flash=0
        this.solids=false
    end,
    update=function(this)
        this.duration-=1
        if this.duration<= 0 then
            destroy_object(this)
        end
    end,
    draw=function(this)
        this.flash+=0.5

        print("1000",this.x-2,this.y,7+this.flash%2)
    end
}
