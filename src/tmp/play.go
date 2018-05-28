/*
* @Author: Yujie Pan
* @Date:   2018-05-28 12:37:27
* @Last Modified by:   Yujie Pan
* @Last Modified time: 2018-05-28 19:23:16
*/
package main

import (
	"fmt"
	"time"
	//_ "github.com/mattn/go-sqlite3"
)

func main() {
	fmt.Println("Hello, World!")
	//db, err := sql.Open("sqlite3", "./playyy.sqlite")
	guess_times := make([]int64, 12)
	guess_times[3] = 2314214214
	fmt.Println(fmt.Sprintf("%d", guess_times))
	t1 := time.Now()
	for i := 0; i < 100000; i++ {
		fmt.Printf("s")
	}
	elapsed := time.Since(t1).Nanoseconds()
	fmt.Println(elapsed)
}
