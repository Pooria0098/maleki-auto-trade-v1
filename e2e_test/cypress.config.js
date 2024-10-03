import fsExtra from 'fs-extra'
import path from 'path'
import { defineConfig } from "cypress";

import db from './sql.js'

function getTestTimestamp() {
  const date = new Date()
  const isoString = date.toISOString();
  const parts = isoString.split(/[T:.]/);
  return `${parts[0]}-${parts[1]}-${parts[2]}-${parts[3]}-${parts[4]}`;
}

const __dirname = new URL('.', import.meta.url).pathname;
const resultDir = path.join(__dirname, 'results', getTestTimestamp())

fsExtra.ensureDirSync(resultDir)

export default defineConfig({
  video: true,
  videosFolder: resultDir ,
  reporter: 'mochawesome',
  reporterOptions: {
    reportDir: resultDir,
    reportFilename: `report.html`,
    overwrite: false,
    html: true,
    json: false,
  },
  e2e: {
    baseUrl: 'http://localhost:5085',
    setupNodeEvents(on) {
      on('task', {
        getUserProfile(email) {
          return new Promise((resolve, reject) => {
            db.get('SELECT * from "auth_user" left join "users_profile" on "auth_user".id = users_profile.user_id  where email = ?', [email], 
              (err, res) => {
              if (err) {
                console.error(err)
                return reject(err)
              }

              if (!res) {
                  reject('no record found')
                }
              return resolve(res)
            })
          })
        }
      })
    },
  },
});

