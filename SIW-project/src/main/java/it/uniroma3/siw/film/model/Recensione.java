package it.uniroma3.siw.film.model;

import static javax.persistence.CascadeType.MERGE;
import static javax.persistence.GenerationType.AUTO;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;
import javax.persistence.ManyToOne;
import javax.validation.constraints.Max;
import javax.validation.constraints.Min;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;

import lombok.Getter;
import lombok.Setter;

@Entity
@Getter @Setter
public class Recensione {
    
    @Id
    @GeneratedValue(strategy = AUTO)
    private Long id;

    @NotBlank
    @Size(min = 2, max = 20)
    private String titolo;

    @NotNull
    @Min(1)
    @Max(5)
    private Short valutazione;

    @NotBlank
    @Size(min = 2, max = 512)
    private String testo;

    @ManyToOne(cascade = MERGE)
    private Film film;

    @ManyToOne(cascade = MERGE)
    private Utente utente;

}
