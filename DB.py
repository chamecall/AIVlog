import pymysql

class DB:
    def __init__(self, hostname, user_name, password, db_name):
        self.hostname = hostname
        self.user_name = user_name
        self.password = password
        self.db_name = db_name
        self.con = pymysql.connect(hostname, user_name, password, cursorclass=pymysql.cursors.DictCursor,
                                   autocommit=True)

        self.cursor = self.con.cursor()
        self.create_db(db_name)

    def exec_query(self, query: str):
        self.cursor.execute(query)
        return self.cursor

    def exec_template_query(self, template, values: tuple):
        self.cursor.execute(template, values)


    def create_db(self, db_name):

        self.exec_query('SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;')
        self.exec_query('SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;')
        self.exec_query("SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';")
        self.exec_query(f"CREATE SCHEMA IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8 ;")
        self.exec_query(f'USE `{db_name}` ;')
        self.exec_query(f'''CREATE TABLE IF NOT EXISTS `Detections` (
                  `detection_id` INT(11) NOT NULL,
                  `frame_num` INT(10) UNSIGNED NOT NULL,
                  `dnn_label` VARCHAR(64) NULL DEFAULT NULL,
                  `box` VARCHAR(32) NULL DEFAULT NULL,
                  PRIMARY KEY (`detection_id`, `frame_num`))
                ENGINE = InnoDB
                DEFAULT CHARACTER SET = utf8;''')
        self.exec_query('''CREATE TABLE IF NOT EXISTS `Labels` (
                  `label_id` INT(11) NOT NULL,
                  `name` VARCHAR(64) NOT NULL,
                  PRIMARY KEY (`label_id`),
                  UNIQUE INDEX `name_UNIQUE` (`name` ASC))
                ENGINE = InnoDB
                DEFAULT CHARACTER SET = utf8;''')

        self.exec_query('''CREATE TABLE IF NOT EXISTS `Assignments` (
                  `frame_num` INT(11) UNSIGNED NOT NULL,
                  `label_id` INT(11) NULL DEFAULT NULL,
                  `detection_id` INT(11) NULL DEFAULT NULL,
                  INDEX `asdf_idx` (`label_id` ASC),
                  INDEX `detection_id_idx` (`detection_id` ASC),
                  CONSTRAINT `detection_id`
                    FOREIGN KEY (`detection_id`)
                    REFERENCES `{db_name}`.`Detections` (`detection_id`)
                    ON DELETE NO ACTION
                    ON UPDATE NO ACTION,
                  CONSTRAINT `label_id`
                    FOREIGN KEY (`label_id`)
                    REFERENCES `{db_name}`.`Labels` (`label_id`)
                    ON DELETE NO ACTION
                    ON UPDATE NO ACTION)
                ENGINE = InnoDB
                DEFAULT CHARACTER SET = utf8;''')

        self.exec_query('SET SQL_MODE=@OLD_SQL_MODE;')
        self.exec_query('SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;')
        self.exec_query('SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;')

