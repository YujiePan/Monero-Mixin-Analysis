package main

import (
	"database/sql"
	"fmt"

	"math/rand"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

func main() {
	r := rand.New(rand.NewSource(time.Now().UnixNano()))
	//var MIX float32 = 5
	//var base_mix_pool_num int = math.Floor((MIX+1)*1.5 + 1)

	db, err := sql.Open("sqlite3", "../DB/tx_in_out_1.sqlite")
	checkErr(err)
	random_num := r.Intn(20000)
	rows, err := db.Query(fmt.Sprintf("SELECT * FROM tx_in_out LIMIT 1 OFFSET %d", random_num))
	checkErr(err)

	for rows.Next() {
		var tx int
		var block int
		err = rows.Scan(&tx, &block)
		checkErr(err)
		fmt.Println(tx, block)
	}
}

/*
func mains() {

	for rows.Next() {
		var tx int
		var block int
		err = rows.Scan(&tx, &block)
		checkErr(err)
		fmt.Println(tx)
		fmt.Println(block)
	}
	db.Close()

}
*/

func checkErr(err error) {
	if err != nil {
		panic(err)
	}
}
