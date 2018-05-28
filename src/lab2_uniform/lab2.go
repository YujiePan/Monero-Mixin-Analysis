/*
* @Author: Yujie Pan
* @Date:   2018-05-28 12:42:26
* @Last Modified by:   Yujie Pan
* @Last Modified time: 2018-05-28 19:44:34
*/
package main

import (
	"database/sql"
	"fmt"
	"math"
	"math/rand"
	"os"
	"sort"
	"strconv"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

var R = rand.New(rand.NewSource(time.Now().UnixNano()))

var SIZE_DB = [...]int{0, 32929106, 33036408, 32872161, 32784690}

var MIX_SIZE int

const SIMU_TIMES int = 250

func main() {
	//var MULTICORE int = runtime.NumCPU() //number of core
	//runtime.GOMAXPROCS(MULTICORE)        //running in multicore
	i, _ := strconv.Atoi(os.Args[1])
	j, _ := strconv.Atoi(os.Args[2])
	MIX_SIZE = j
	fmt.Println("THREAD: %d")
	fmt.Println("MIXIN: %d")
	var info string
	simulate(i, j, SIZE_DB[i], &info, SIMU_TIMES)
	appendToFile(i, fmt.Sprintf("../../result/lab2-th%d-mix%d.txt", i, MIX_SIZE), info)

	/*for i := 1; i < THREAD_NUM+1; i++ {
		go simulate(i, MIX_SIZE, SIZE_DB[i], info, SIMU_TIMES)
	}
	for i := 1; i < THREAD_NUM+1; i++ {
		appendToFile(i, fmt.Sprintf("lab2-th%d-mix%d.txt", i, MIX_SIZE), <-info)
	}*/
}

func WriteWithIoutil(i int, name, content string) {
	f, err := os.Create(name)
	checkErr(err)
	defer f.Close()
	n3, err := f.WriteString(content)
	fmt.Printf("wrote %d bytes\n", n3)
	f.Sync()
}

func appendToFile(i int, name string, content string) error {
	f, err := os.OpenFile(name, os.O_WRONLY, 0644)
	if err != nil {
		fmt.Println("creating: ")
		ff, err := os.Create(name)
		checkErr(err)
		ff.Close()
		f, err = os.OpenFile(name, os.O_WRONLY, 0644)
	}
	n, _ := f.Seek(0, os.SEEK_END)
	_, err = f.WriteAt([]byte(fmt.Sprintf("[%s]TH%d:\n%s\r\n",
		time.Now().Format("2006-01-02 15:04:05"), i, content)), n)

	defer f.Close()
	return err
}

func rand_choose_from_db(db *sql.DB, random_num int) (tx_dest int, tx_src int, src_id int) {
	rows, err := db.Query(fmt.Sprintf("SELECT * FROM tx_in_out LIMIT 1 OFFSET %d", random_num))
	checkErr(err)
	if rows.Next() {
		/*
			var tx_dest int
			var tx_src int
			var src_id int
		*/
		err = rows.Scan(&tx_dest, &tx_src, &src_id)
		checkErr(err)
		return tx_dest, tx_src, src_id
	}
	return 0, 0, 0

}

func mini_tx_id(db *sql.DB, tx int, n int) (block_id int, mini_id int) {
	rows, err := db.Query(fmt.Sprintf("SELECT * FROM TXTOBLOCK WHERE txid = %d", tx))
	checkErr(err)
	if rows.Next() {
		var x int
		err = rows.Scan(&x, &block_id, &mini_id)
		checkErr(err)
		mini_id += n
		return block_id, mini_id
	}
	return 3, 3
}

func mini_tx_id_2_block(db *sql.DB, mini_id int) (block_id int) {
	rows, err := db.Query(fmt.Sprintf(
		"SELECT * FROM TXTOBLOCK WHERE MINITX_STARTING <= %d ORDER BY block desc LIMIT 1", mini_id))
	checkErr(err)
	rows.Next()
	var x int
	err = rows.Scan(&x, &block_id, &mini_id)
	checkErr(err)
	return block_id
}

func simulate(thread_id int, MIX int, max_random int, info *string, SIMU_TIMES int) {
	t1 := time.Now() // get current time
	DB_TX_IN_OUT_PATH := fmt.Sprintf("../../db/new_tx_in_out%d.sqlite", thread_id)
	DB_TX_BL_PATH := fmt.Sprintf("../../db/new_tx_block.sqlite")
	pool_size := int(math.Floor(float64(MIX+1)*1.5 + 1))
	pool_size = MIX
	// to simplify

	db_record, err := sql.Open("sqlite3", DB_TX_IN_OUT_PATH)
	db_find_block, err := sql.Open("sqlite3", DB_TX_BL_PATH)
	checkErr(err)

	guess_times := make([]int, MIX+2)
	guess_times[0] = 0

	for k := 0; k < SIMU_TIMES; k++ {
		if int(k%10) == int(0) {
			elapsed := time.Since(t1).Nanoseconds()
			fmt.Println(fmt.Sprintf("TH-%d: MIX-%d: TIME-%d: TOTAL-%d",
				thread_id, MIX, k, SIMU_TIMES))
			more := (elapsed) / int64(k+1) * int64(SIMU_TIMES-k)
			fmt.Println(more)
			fmt.Printf("USED TIME: %ds \tREMAIN: %ds\n\n", elapsed/1e9, more/1e9)
		}
		selected_mini := make([]int, pool_size+1)
		row_prob := make([]float32, pool_size+1)

		now_tx, real_out, real_out_n := rand_choose_from_db(db_record, R.Intn(SIZE_DB[thread_id]-1))
		for now_tx == 0 {
			now_tx, real_out, real_out_n = rand_choose_from_db(db_record, R.Intn(SIZE_DB[thread_id]-1))
		}

		_, real_mini_id := mini_tx_id(db_find_block, real_out, real_out_n)
		_, now_mini_id := mini_tx_id(db_find_block, now_tx, 0)

		//fmt.Println("TH", thread_id, "Random Choose:", now_tx, "from", real_out, real_out_n, "mini_id", real_mini_id)
		row_prob[0] = 1
		selected_mini[0] = real_mini_id

		for j := 0; j < pool_size; j++ {
			sample := R.Intn(now_mini_id - 1)
			for sample < 100 || is_in_array(selected_mini, sample, 1, j) {
				sample = R.Intn(SIZE_DB[thread_id] - 1)
			}
			selected_mini[j+1] = sample
		}
		//fmt.Println("\tTH", thread_id, "choose_miniid:", selected_mini)
		sort.Ints(selected_mini)
		guess_time := find_index(selected_mini, real_mini_id, MIX)
		guess_times[MIX+1-guess_time] += 1
		//fmt.Println("\tTH", thread_id, "final:", now_tx, "from", real_out, real_out_n, "guess time:", MIX+1-guess_time)
	}
	*info = fmt.Sprintf("OK: %d", guess_times)
}

func checkErr(err error) {
	if err != nil {
		panic(err)
	}
}

func is_in_array(arr []int, element int, start int, end int) bool {
	for i := start; i <= end; i++ {
		if arr[i] == element {
			return true
		}
	}
	return false
}

func find_index(arr []int, element int, largest int) int {
	for i := largest; i >= 0; i-- {
		if arr[i] == element {
			return i
		}
	}
	return -1
}
