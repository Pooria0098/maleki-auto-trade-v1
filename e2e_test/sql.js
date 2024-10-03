import sqlite3 from 'sqlite3'

const db = new (sqlite3.verbose()).Database('/tmp/db.sqlite3', sqlite3.OPEN_READONLY, (err) => {
    if (err) {
      process.exit(1)
    }


    console.log("database connected")
  }
)

export default db
