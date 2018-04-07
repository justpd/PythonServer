using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Bindings;

namespace ConsoleApp.Chars
{
    class Preacher : UserChar
    {
        public Preacher(UserChar baseChar)
        {
            id = baseChar.id;
            name = baseChar.name;
            Health = baseChar.Health;
            Agility = baseChar.Agility;
            Strength = baseChar.Strength;
            Intelligence = baseChar.Intelligence;
            Potency = baseChar.Potency;
            Tenacity = baseChar.Tenacity;
            CriticalChance = baseChar.CriticalChance;
            HealthSteal = baseChar.HealthSteal;
            Armor = baseChar.Armor;
            MagicResistance = baseChar.MagicResistance;
            ArmorPenetration = baseChar.ArmorPenetration;
            EvadeChance = baseChar.EvadeChance;
            Speed = baseChar.Agility;
            HealForce = baseChar.HealForce;
            CriticalDamage = baseChar.CriticalDamage;
            PhysicalDamage = baseChar.PhysicalDamage;
            MagicalDamage = baseChar.MagicalDamage;
            skillCount = 2;
        }

        public override void Skill_1(UserChar target, QuickPlaySession session)
        {
            session.moveLogs.Add(target.GetPhysicalDamage(this));
        }

        public override void Skill_2(UserChar target, QuickPlaySession session)
        {
            
            session.moveLogs.Add(target.GetMagicalDamage(this));
        }
    }
}
