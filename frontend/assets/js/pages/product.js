(async function(){
    try{
        const res = await fetch("/api/product/1");
        if (!res.ok) throw new Error (`HTTP ${res.status}`);
        const json = await res.json();
        console.log(json)
    }catch (err){
        console.error(err);
        console.log("faile")
    }
})();