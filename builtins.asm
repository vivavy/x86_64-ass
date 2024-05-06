; hack for FASM to allow primitive arrays, specifically for strings here

struc string val {
    common
    local .value
    dq .value
.value:
    if ~val eq
        db val
    end if
    db 0
}

