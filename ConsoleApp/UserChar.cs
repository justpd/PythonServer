using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Bindings;
using Newtonsoft.Json;

namespace ConsoleApp
{
    public class UserChar
    {
        public string name;
        public string id;
        public int lvl;
        public int power;

        public int Health;
        public int Agility;
        public int Strength;
        public int Intelligence;
        public float Potency;
        public float Tenacity;
        public float CriticalChance;
        public float HealthSteal;
        public float Armor;
        public float MagicResistance;
        public float ArmorPenetration;
        public float EvadeChance;
        public float Speed;

        public float HealForce;
        public float CriticalDamage;
        public float PhysicalDamage;
        public float MagicalDamage;

        public bool isActive = true;

        public int health;
        public int agility;
        public int strength;
        public int intelligence;
        public float potency;
        public float tenacity;
        public float criticalChance;
        public float healthSteal;
        public float armor;
        public float magicResistance;
        public float armorPenetration;
        public float evadeChance;
        public float speed;

        public float healForce;
        public float criticalDamage;
        public float physicalDamage;
        public float magicalDamage;
        public float turnmeter = 0.0F;

        public int skillCount;

        Random random = new Random();

        public void SetBaseValues()
        {
            health = Health;
            agility = Agility;
            strength = Strength;
            intelligence = Intelligence;
            potency = Potency;
            tenacity = Tenacity;
            criticalChance = CriticalChance;
            healthSteal = HealthSteal;
            armor = Armor;
            magicResistance = MagicResistance;
            armorPenetration = ArmorPenetration;
            evadeChance = EvadeChance;
            speed = Agility;
            healForce = HealForce;
            criticalDamage = CriticalDamage;
            physicalDamage = PhysicalDamage;
            magicalDamage = MagicalDamage;
        }

        public int CalculatePower()
        {
            int gs = 0;
            return gs;
        }

        public static string GetIdByName(string name)
        {
            switch (name)
            {
                case "Paladin":
                    return "T00";
                case "Preacher":
                    return "T01";
                case "Priest":
                    return "T02";
                default:
                    return "T00";
            }
        }

        public void Perform(int skill, UserChar target, QuickPlaySession session)
        {
            switch (skill)
            {
                case 1:
                    Skill_1(target, session);
                    break;
            }
        }

        public virtual void Skill_1(UserChar target, QuickPlaySession session)
        {
            session.moveLogs.Add(target.GetPhysicalDamage(this));
        }

        public virtual void Skill_2(UserChar target, QuickPlaySession session)
        {

        }

        public virtual void Skill_3(UserChar target, QuickPlaySession session)
        {

        }

        public double GetRandomFloat(double minimum, double maximum)
        {
            return random.NextDouble() * (maximum - minimum) + minimum;
        }

        public MoveLog GetPhysicalDamage(UserChar enemy)
        {
            MoveLog moveLog = new MoveLog
            {
                type = "Damage",
                current = id,
                target = enemy.id
            };
            if (GetRandomFloat(1.0F, 100.0F) > evadeChance)
            {
                moveLog.damage = (int)(enemy.physicalDamage * (0.9F * enemy.strength + (0.002F * enemy.strength * GetRandomFloat(0.0F, 100.0F))));

                Console.WriteLine(GetRandomFloat(1.0F, 100.0F) + "|" + enemy.criticalChance);
                if (GetRandomFloat(1.0F, 100.0F) < enemy.criticalChance)
                {
                    Console.WriteLine(moveLog.damage);
                    moveLog.damage = (int)((moveLog.damage * enemy.criticalDamage));
                    Console.WriteLine(moveLog.damage);
                    moveLog.isCritical = true;
                }

                float totalArmor = armor - enemy.armorPenetration;
                if (totalArmor < 0) totalArmor = 0;

                moveLog.damage = (int)(moveLog.damage * (100 - totalArmor) / 100);
                health -= moveLog.damage;

                moveLog.heal = (int)(moveLog.damage * enemy.healthSteal / 100);
                enemy.health += moveLog.heal;


                if (moveLog.isCritical)
                    Console.WriteLine(id + ": critical damage " + moveLog.damage);
                else
                    Console.WriteLine(id + ": damage " + moveLog.damage);

                if (moveLog.heal > 0)
                    Console.WriteLine(enemy.id + ": health steal " + moveLog.heal);

                return moveLog;
            }
            else
            {
                moveLog.isEvaded = true;
                Console.WriteLine(id + " evaded.");
            }

            return moveLog;
        }

        public MoveLog GetMagicalDamage(UserChar enemy)
        {
            MoveLog moveLog = new MoveLog
            {
                type = "MagicalDamage",
                current = enemy.id,
                target = id
            };
            Console.WriteLine(GetRandomFloat(1.0F, 100.0F));
            if (GetRandomFloat(1.0F, 100.0F) > evadeChance)
            {
                moveLog.damage = (int)(enemy.magicalDamage * (0.9F * enemy.intelligence + (0.002F * enemy.intelligence * GetRandomFloat(0.0F, 100.0F))));
                if (GetRandomFloat(1.0F, 100.0F) < enemy.criticalChance)
                {
                    moveLog.damage = (int)(moveLog.damage * (float)enemy.criticalDamage);
                    moveLog.isCritical = true;
                }

                moveLog.damage = (int)(moveLog.damage * (100 - magicResistance) / 100);
                health -= moveLog.damage;

                moveLog.heal = (int)(moveLog.damage * enemy.healthSteal / 100);
                enemy.health += moveLog.heal;


                if (moveLog.isCritical)
                    Console.WriteLine(id + ": critical damage " + moveLog.damage);
                else
                    Console.WriteLine(id + ": damage " + moveLog.damage);

                if (moveLog.heal > 0)
                    Console.WriteLine(enemy.id + ": health steal " + moveLog.heal);

                return moveLog;
            }
            else
            {
                moveLog.isEvaded = true;
                Console.WriteLine(id + " evaded.");
            }

            return moveLog;
        }

        public virtual MoveLog Heal(UserChar teamMate)
        {
            MoveLog moveLog = new MoveLog
            {
                type = "Heal",
                current = id,
                target = teamMate.id
            };
            moveLog.heal = (int)(0.9F * healForce + (0.002F * healForce * GetRandomFloat(0.0F, 100.0F)));
            teamMate.health += moveLog.heal;
            Console.WriteLine(teamMate.id + ": heal " + moveLog.heal);

            return moveLog;
        }

        public virtual MoveLog PureHeal(UserChar teamMate, int heal)
        {
            MoveLog moveLog = new MoveLog
            {
                type = "PureHeal",
                current = id,
                target = teamMate.id
            };

            moveLog.heal = (int)(0.9F * heal + (0.002F * heal * GetRandomFloat(0.0F, 100.0F)));
            teamMate.health += moveLog.heal;
            Console.WriteLine(teamMate.id + ": Pure heal " + moveLog.heal);

            return moveLog;
        }

        public void CheckValues()
        {
            if (health < 0) health = 0;
            else if (health > Health) health = Health;
            if (agility < 0) agility = 0;
            if (strength < 0) strength = 0;
            if (intelligence < 0) intelligence = 0;
            if (potency < 0) potency = 0;
            if (tenacity < 0) tenacity = 0;
            if (criticalChance < 0) criticalChance = 0;
            else if (criticalChance > 100.0F) criticalChance = 100.0F;
            if (healthSteal < 0) healthSteal = 0;
            if (armor < 0) armor = 0;
            else if (armor > 100.0F) armor = 100.0F;
            if (magicResistance < 0) magicResistance = 0;
            else if (magicResistance > 100.0F) magicResistance = 100.0F;
            if (armorPenetration < 0) armorPenetration = 0;
            else if (armorPenetration > 100.0F) armorPenetration = 100.0F;
            if (evadeChance < 0) evadeChance = 0;
            else if (evadeChance > 100.0F) evadeChance = 100.0F;
            if (speed < 0) speed = 0;
            if (healForce < 0) healForce = 0;
            if (criticalDamage < 0) criticalDamage = 0;
            if (physicalDamage < 0) physicalDamage = 0;
            if (magicalDamage < 0) magicalDamage = 0;
            if (turnmeter <= 0.01F) turnmeter = 0.01F;
            else if (turnmeter > 100.0F) turnmeter = 100.0F;
        }
    }

}
