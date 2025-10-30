* =======================================================
* Program：ConceptualNetwork
* Date：Sep 24, 2025
* =======================================================

clear all
clear matrix
set more off

global root = "E:\Guxinfeng\Documents\Study\2025_Fall\Shugar_project\conceptual_network"

*** Step 1 – Process text dataset:
import excel "$root\data\anes_timeseries_2016_redacted_openends.xlsx", sheet("V161069") firstrow clear
save master.dta, replace

* Loop through other sheets
foreach s in V161072 V161075 V161078 ///
	V161098 V161101 V161104 V161106 {
    import excel "$root\data\anes_timeseries_2016_redacted_openends.xlsx", sheet("`s'") firstrow clear
    save temp.dta, replace
    
    use master.dta, clear
    merge 1:1 HOVERHEREFORNOTEV160001 using temp.dta

    drop _merge
    save master.dta, replace
}

use master.dta, clear

* Check duplicates on key
duplicates report HOVERHEREFORNOTEV160001
duplicates list HOVERHEREFORNOTEV160001

* Rename variables
foreach var of varlist _all {
    local newname = substr("`var'", 1, 7)
    if "`newname'" != "`var'" {
        rename `var' `newname'
    }
}

rename HOVER* V160001_orig

destring V160001_orig, replace

save "$root\data\anes_2016_text.dta", replace

*** Step 2 – Constructing the characteristic variables: 

use "$root\data\anes_timeseries_2016_Stata13.dta", clear

** 2.1 Demographics

*Age
gen age = V161267 if V161267 > 0
sum age

*Gender
gen female = . if V161342==-9
replace female = 0 if V161342==1 | V161342==3
replace female = 1 if V161342==2
tab female

*Education
gen education = V161270
for var education: replace X =. if inlist(X, -9, 90, 95)
*Recode education into three levels
replace education = 1 if education<10
replace education = 2 if education>9 & education<13
replace education = 3 if education>12

** 2.2 Political engagement

*Ideology
gen leftright =  V161158x - 1
for var leftright: replace X =. if inlist(X, -10, -9)
tab leftright

*Political interest
gen politicalinterest = V162256*-1 + 4 if V162256 > 0
tab politicalinterest, m

*Political participation
gen V162018a_rev = V162018a*-1 + 2 if V162018a > 0
gen V162018b_rev = V162018b*-1 + 2 if V162018b > 0
egen politicalparticipation_ = rowtotal(V162018a_rev V162018b_rev)
gen politicalparticipation = politicalparticipation_/2
sum politicalparticipation

** 2.3 Personality
gen V162338_rev = 8 - V162338 if V162338 > 0
gen V162334_rev = 8 - V162334 if V162334 > 0
gen V162340_rev = 8 - V162340 if V162340 > 0
gen V162341_rev = 8 - V162341 if V162341 > 0
gen V162342_rev = 8 - V162342 if V162342 > 0

gen TIPI_extraversion = (V162333 + V162338_rev)/2 if V162333 > 0
gen TIPI_agreeableness = (V162339 + V162334_rev)/2 if V162339 > 0
gen TIPI_conscientiousness = (V162335 + V162340_rev) / 2
gen TIPI_emotionalstability = (V162336 + V162341_rev) / 2
gen TIPI_openness = (V162337 + V162342_rev) / 2

keep V160001 V160001_orig age female education ///
	leftright politicalinterest politicalparticipation TIPI*

*** Step 3 – Merge text and non-text dataset:

isid V160001_orig
merge 1:1 V160001_orig using "$root\data\anes_2016_text.dta"

list V160001 if _merge==2
drop if _merge==2
drop _merge

save "$root\data\anes_2016.dta", replace

********

use "$root\data\anes_2016.dta", clear
codebook  V161069- V161106

count if !missing(V161069, V161072, V161075, V161078, V161098, V161101, V161104, V161106)
count if !missing(V161069, V161072)
count if !missing(V161069, V161072, V161075, V161078)





