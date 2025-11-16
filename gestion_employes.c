/*
 * Systeme de Gestion de Donnees - Application CRUD en C
 * Auteur: Corneille Ligan
 * Description: Gestion complete d'une base de donnees d'employes
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_EMPLOYES 100
#define LONGUEUR_NOM 50
#define FICHIER_DONNEES "employes.csv"

/* Structure pour representer un employe */
typedef struct {
    int id;
    char nom[LONGUEUR_NOM];
    char poste[LONGUEUR_NOM];
    float salaire;
    int actif;
} Employe;

/* Variables globales */
Employe employes[MAX_EMPLOYES];
int nombreEmployes = 0;

/* Prototypes de fonctions */
void afficherMenu();
void ajouterEmploye();
void afficherEmployes();
void modifierEmploye();
void supprimerEmploye();
void rechercherEmploye();
void sauvegarderDonnees();
void chargerDonnees();
void afficherLigne();

/* Fonction principale */
int main() {
    int choix;
    
    chargerDonnees();
    
    do {
        afficherMenu();
        printf("Votre choix: ");
        scanf("%d", &choix);
        getchar();
        
        switch(choix) {
            case 1:
                ajouterEmploye();
                break;
            case 2:
                afficherEmployes();
                break;
            case 3:
                modifierEmploye();
                break;
            case 4:
                supprimerEmploye();
                break;
            case 5:
                rechercherEmploye();
                break;
            case 0:
                sauvegarderDonnees();
                printf("\nDonnees sauvegardees. Au revoir!\n");
                break;
            default:
                printf("\nChoix invalide!\n");
        }
        
        if(choix != 0) {
            printf("\nAppuyez sur Entree pour continuer...");
            getchar();
        }
        
    } while(choix != 0);
    
    return 0;
}

/* Afficher le menu principal */
void afficherMenu() {
    system("clear");
    printf("\n");
    afficherLigne();
    printf("         SYSTEME DE GESTION DES EMPLOYES\n");
    afficherLigne();
    printf("  1. Ajouter un employe\n");
    printf("  2. Afficher tous les employes\n");
    printf("  3. Modifier un employe\n");
    printf("  4. Supprimer un employe\n");
    printf("  5. Rechercher un employe\n");
    printf("  0. Quitter\n");
    afficherLigne();
    printf("  Total: %d employe(s)\n", nombreEmployes);
    afficherLigne();
    printf("\n");
}

/* Ajouter un nouvel employe */
void ajouterEmploye() {
    if(nombreEmployes >= MAX_EMPLOYES) {
        printf("\nBase de donnees pleine!\n");
        return;
    }
    
    Employe nouvel;
    nouvel.id = nombreEmployes + 1;
    nouvel.actif = 1;
    
    printf("\n=== AJOUT D'UN EMPLOYE ===\n\n");
    printf("Nom: ");
    fgets(nouvel.nom, LONGUEUR_NOM, stdin);
    nouvel.nom[strcspn(nouvel.nom, "\n")] = 0;
    
    printf("Poste: ");
    fgets(nouvel.poste, LONGUEUR_NOM, stdin);
    nouvel.poste[strcspn(nouvel.poste, "\n")] = 0;
    
    printf("Salaire: ");
    scanf("%f", &nouvel.salaire);
    getchar();
    
    employes[nombreEmployes++] = nouvel;
    sauvegarderDonnees();
    
    printf("\nEmploye ajoute avec succes! (ID: %d)\n", nouvel.id);
}

/* Afficher tous les employes */
void afficherEmployes() {
    if(nombreEmployes == 0) {
        printf("\nAucun employe enregistre.\n");
        return;
    }
    
    printf("\n=== LISTE DES EMPLOYES ===\n\n");
    printf("%-5s %-20s %-20s %-12s\n", "ID", "Nom", "Poste", "Salaire");
    printf("------------------------------------------------------------\n");
    
    for(int i = 0; i < nombreEmployes; i++) {
        if(employes[i].actif) {
            printf("%-5d %-20s %-20s %.2f euros\n",
                   employes[i].id,
                   employes[i].nom,
                   employes[i].poste,
                   employes[i].salaire);
        }
    }
}

/* Modifier un employe */
void modifierEmploye() {
    int id;
    printf("\n=== MODIFICATION D'UN EMPLOYE ===\n\n");
    printf("ID de l'employe: ");
    scanf("%d", &id);
    getchar();
    
    for(int i = 0; i < nombreEmployes; i++) {
        if(employes[i].id == id && employes[i].actif) {
            printf("\nNouveau nom (actuel: %s): ", employes[i].nom);
            fgets(employes[i].nom, LONGUEUR_NOM, stdin);
            employes[i].nom[strcspn(employes[i].nom, "\n")] = 0;
            
            printf("Nouveau poste (actuel: %s): ", employes[i].poste);
            fgets(employes[i].poste, LONGUEUR_NOM, stdin);
            employes[i].poste[strcspn(employes[i].poste, "\n")] = 0;
            
            printf("Nouveau salaire (actuel: %.2f): ", employes[i].salaire);
            scanf("%f", &employes[i].salaire);
            
            sauvegarderDonnees();
            printf("\nEmploye modifie avec succes!\n");
            return;
        }
    }
    printf("\nEmploye introuvable!\n");
}

/* Supprimer un employe */
void supprimerEmploye() {
    int id;
    char confirmation;
    
    printf("\n=== SUPPRESSION D'UN EMPLOYE ===\n\n");
    printf("ID de l'employe: ");
    scanf("%d", &id);
    getchar();
    
    for(int i = 0; i < nombreEmployes; i++) {
        if(employes[i].id == id && employes[i].actif) {
            printf("\nConfirmer la suppression de %s? (O/N): ", employes[i].nom);
            scanf("%c", &confirmation);
            
            if(confirmation == 'O' || confirmation == 'o') {
                employes[i].actif = 0;
                sauvegarderDonnees();
                printf("\nEmploye supprime avec succes!\n");
            } else {
                printf("\nSuppression annulee.\n");
            }
            return;
        }
    }
    printf("\nEmploye introuvable!\n");
}

/* Rechercher un employe */
void rechercherEmploye() {
    char recherche[LONGUEUR_NOM];
    int trouve = 0;
    
    printf("\n=== RECHERCHE D'EMPLOYE ===\n\n");
    printf("Nom a rechercher: ");
    fgets(recherche, LONGUEUR_NOM, stdin);
    recherche[strcspn(recherche, "\n")] = 0;
    
    printf("\n%-5s %-20s %-20s %-12s\n", "ID", "Nom", "Poste", "Salaire");
    printf("------------------------------------------------------------\n");
    
    for(int i = 0; i < nombreEmployes; i++) {
        if(employes[i].actif && strstr(employes[i].nom, recherche) != NULL) {
            printf("%-5d %-20s %-20s %.2f euros\n",
                   employes[i].id,
                   employes[i].nom,
                   employes[i].poste,
                   employes[i].salaire);
            trouve = 1;
        }
    }
    
    if(!trouve) {
        printf("Aucun employe trouve.\n");
    }
}

/* Sauvegarder les donnees dans un fichier CSV */
void sauvegarderDonnees() {
    FILE *fichier = fopen(FICHIER_DONNEES, "w");
    if(fichier == NULL) {
        printf("Erreur: Impossible de sauvegarder les donnees\n");
        return;
    }
    
    /* Ecrire l'en-tete CSV */
    fprintf(fichier, "ID,Nom,Poste,Salaire,Actif\n");
    
    /* Ecrire chaque employe */
    for(int i = 0; i < nombreEmployes; i++) {
        fprintf(fichier, "%d,%s,%s,%.2f,%d\n",
                employes[i].id,
                employes[i].nom,
                employes[i].poste,
                employes[i].salaire,
                employes[i].actif);
    }
    
    fclose(fichier);
}

/* Charger les donnees depuis un fichier CSV */
void chargerDonnees() {
    FILE *fichier = fopen(FICHIER_DONNEES, "r");
    if(fichier == NULL) return;
    
    char ligne[200];
    
    /* Ignorer la premiere ligne (en-tete) */
    fgets(ligne, sizeof(ligne), fichier);
    
    /* Lire chaque ligne */
    nombreEmployes = 0;
    while(fgets(ligne, sizeof(ligne), fichier) && nombreEmployes < MAX_EMPLOYES) {
        sscanf(ligne, "%d,%[^,],%[^,],%f,%d",
               &employes[nombreEmployes].id,
               employes[nombreEmployes].nom,
               employes[nombreEmployes].poste,
               &employes[nombreEmployes].salaire,
               &employes[nombreEmployes].actif);
        nombreEmployes++;
    }
    
    fclose(fichier);
}

/* Afficher une ligne decorative */
void afficherLigne() {
    printf("====================================================\n");
}
